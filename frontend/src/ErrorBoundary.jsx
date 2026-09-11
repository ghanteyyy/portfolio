import React from 'react';

export default class ErrorBoundary extends React.Component {
	state = { failed: false };
	static getDerivedStateFromError() {
		return { failed: true };
	}
	render() {
		if (this.state.failed) {
			return (
				<div className="load-screen" role="alert">
					<h1>Something went wrong.</h1>
					<p>Please reload the page to try again.</p>
					<button className="button dark" onClick={() => window.location.reload()}>
						Reload page
					</button>
				</div>
			);
		}
		return this.props.children;
	}
}
