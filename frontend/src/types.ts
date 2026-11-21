export interface CurrentUser {
  id: string
  name: string
  role: 'super_user' | 'family' | string
}

export interface Bucket {
  id: string
  name: string
  bucket_type: 'OPEN' | 'PERSONAL' | string
}

export interface BucketsResponse {
  buckets: Bucket[]
}

export interface StoredFile {
  filename: string
  size: number
  last_modified: string | null
}

export interface BucketFilesResponse {
  bucket_id: string
  bucket_name: string
  bucket_type: string
  files: StoredFile[]
}
