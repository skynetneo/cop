export function searchResources(
  query: string,
  options: { limit?: number; offset?: number } = {}
) {
  const { limit = 10, offset = 0 } = options;

  return fetch(`/api/resources/search?query=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => data.resources);
}