// Bound network waits so forms can recover from a stalled connection.
export async function request(url, options = {}) {
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), 30000);
	try {
		return await fetch(url, { ...options, signal: controller.signal });
	} catch (error) {
		if (error.name === 'AbortError') {
			throw new Error('The connection timed out. Please try again.');
		}
		throw error;
	} finally {
		clearTimeout(timer);
	}
}
