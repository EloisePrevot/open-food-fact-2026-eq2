export const ensureSuccess = async (response: Response): Promise<void> => {
  if (!response.ok) {
    throw new Error(await errorMessage(response))
  }
}

const errorMessage = async (response: Response): Promise<string> => {
  const body = await response.json().catch(() => null)
  return body?.message ?? `The API returned status ${response.status}.`
}
