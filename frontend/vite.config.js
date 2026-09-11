import { defineConfig } from 'vite';
export default defineConfig({
	server: {
		proxy: {
			'/media': 'http://127.0.0.1:8000',
			'/api': 'http://127.0.0.1:8000',
			'/resume/': 'http://127.0.0.1:8000',
		},
	},
	build: { outDir: 'dist' },
});
