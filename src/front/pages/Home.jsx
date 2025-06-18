import React, { useEffect } from "react"
import rigoImageUrl from "../assets/img/rigo-baby.jpg";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { Navigate } from "react-router-dom";

export const Home = () => {

	const { store, dispatch } = useGlobalReducer()

	if (!store.token) {
		return <Navigate to="/login" /> // redirecciona a otra vista
	}
	return (
		<div className="container">
			<div>
				<h1>WELCOME</h1>
				<p className="mt-4">You have logged in</p>
			</div>
		</div>
	);
}; 