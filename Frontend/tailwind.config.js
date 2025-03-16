const flowbite = require('flowbite-react/tailwind');

/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		'./public/index.html', './src/**/*.{js,jsx}', 
		flowbite.content()
	],
	theme: {
		extend: {},
	},
	plugins: [flowbite.plugin()],
};
