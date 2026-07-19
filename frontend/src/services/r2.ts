/**
 * Service: Upload de arquivos para o R2 (Cloudflare).
 *
 * Uso:
 *   const presignedUrl = await getUploadUrl({ filename, wedding_id });
 *   await uploadFileToR2(presignedUrl.data.upload_url, file);
 */

export async function uploadFileToR2(
  presignedUrl: string,
  file: File,
): Promise<void> {
  const response = await fetch(presignedUrl, {
    method: "PUT",
    body: file,
    headers: { "Content-Type": file.type || "application/octet-stream" },
  });

  if (!response.ok) {
    throw new Error(
      `Upload failed: ${response.status} ${response.statusText}`,
    );
  }
}
