
import bcrypt

from db.database import async_session
from db.models.bucket import Buckets, BucketType
from db.models.user import AccountType, User

from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend

from sqlalchemy import select
from starlette.requests import Request

from storage.minio_client import create_bucket

from wtforms import FloatField, PasswordField
from wtforms.validators import InputRequired, NumberRange


GB = 1024 ** 3


class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        async with async_session() as db:
            result = await db.execute(
                select(User).where(User.name == username)
            )
            user = result.scalar_one_or_none()

            if not user or user.account_type != AccountType.SUPER_USER:
                return False

            if not bcrypt.checkpw(
                str(password).encode("utf-8"),
                user.password_hash.encode("utf-8"),
            ):
                return False

            request.session.update({
                "admin_user_id": str(user.id)
            })

            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "admin_user_id" in request.session


class UserAdmin(ModelView, model=User):

    name = "Пользователь"
    name_plural = "Пользователи"

    column_list = [
        User.id,
        User.name,
        User.email,
        User.account_type,
        User.is_approved,
        User.created_at,
    ]

    column_searchable_list = [
        User.name,
        User.email,
    ]

    column_labels = {
        "name": "Имя",
        "email": "Email",
        "password_hash": "Пароль",
        "account_type": "Роль",
        "is_approved": "Подтверждён",
        "created_at": "Дата создания",
    }

    form_overrides = {
        "password_hash": PasswordField,
    }

    form_excluded_columns = [
        "created_at",
        "buckets",
    ]

    async def on_model_change(
        self,
        data: dict,
        model: User,
        is_created: bool,
        request: Request,
    ) -> None:

        raw_password = data.get("password_hash")

        if raw_password:
            if not raw_password.startswith("$2b$"):
                salt = bcrypt.gensalt()

                hashed = bcrypt.hashpw(
                    raw_password.encode("utf-8"),
                    salt,
                ).decode("utf-8")

                model.password_hash = hashed
                data["password_hash"] = hashed

        elif is_created:
            raise ValueError(
                "Необходимо указать пароль для нового пользователя"
            )

        else:
            data.pop("password_hash", None)

    async def after_model_change(
        self,
        data: dict,
        model: User,
        is_created: bool,
        request: Request,
    ) -> None:

        if is_created:
            default_bucket_name = "personal"

            create_bucket(f"{model.id}-{default_bucket_name}")

            async with async_session() as db:
                new_bucket = Buckets(
                    name=default_bucket_name,
                    bucket_type=BucketType.PERSONAL,
                    owner_id=model.id,
                    quota_bytes=1 * GB,
                )

                db.add(new_bucket)
                await db.commit()


class BucketAdmin(ModelView, model=Buckets):

    name = "Бакет"
    name_plural = "Бакеты и квоты"

    column_list = [
        Buckets.id,
        Buckets.name,
        Buckets.bucket_type,
        Buckets.owner,
        Buckets.quota_bytes,
    ]

    column_formatters = {
        Buckets.quota_bytes: lambda m, a: (
            f"{round((m.quota_bytes or 0) / GB, 2)} ГБ"
        ),
    }

    column_labels = {
        "name": "Имя бакета",
        "bucket_type": "Тип доступа",
        "owner": "Владелец",
        "quota_bytes": "Квота хранилища (ГБ)",
    }

    form_overrides = {
        "quota_bytes": FloatField,
    }

    form_excluded_columns = [
        "created_at",
    ]

    form_args = {
        "quota_bytes": {
            "validators": [
                InputRequired(message="Укажите квоту в ГБ"),
                NumberRange(min=0.01),
            ],
        },
    }

    async def scaffold_form(self, rules=None):

        form_class = await super().scaffold_form(rules)

        orig_init = form_class.__init__

        def custom_init(form_self, *args, **kwargs):

            orig_init(form_self, *args, **kwargs)

            formdata = kwargs.get("formdata")

            if formdata is None and args:
                formdata = args[0]

            if formdata is not None:
                return

            if form_self.quota_bytes.data is not None:
                form_self.quota_bytes.data = round(
                    float(form_self.quota_bytes.data) / GB,
                    2,
                )

        form_class.__init__ = custom_init

        return form_class

    async def on_model_change(
        self,
        data: dict,
        model: Buckets,
        is_created: bool,
        request: Request,
    ) -> None:

        quota_gb = data.get("quota_bytes")

        if quota_gb is not None:
            bytes_val = int(float(quota_gb) * GB)

            model.quota_bytes = bytes_val
            data["quota_bytes"] = bytes_val

        if is_created:

            owner_val = data.get("owner") or data.get("owner_id")

            if hasattr(owner_val, "id"):
                prefix = str(owner_val.id)

            elif owner_val:
                prefix = str(owner_val)

            else:
                prefix = "shared"

            bucket_name = data.get("name", model.name)

            create_bucket(f"{prefix}-{bucket_name}")
