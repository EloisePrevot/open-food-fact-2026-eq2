export const ensureSuccess = async (response: Response): Promise<void> => {
  if (!response.ok) {
    throw new Error(`The API returned status ${response.status}.`)
  }
}
