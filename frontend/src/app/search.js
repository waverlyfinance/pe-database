// NO LONGER USED. Using ShadCN component instead

import React, { useState, useEffect } from "react";

export default function Search ({ onSearchChange }) {
    // set state
    const [searchQuery, setSearchQuery] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault(); // prevent the default form submit action, which refreshes the page
        onSearchChange(searchQuery); // passes the current state back to the Parent homepage. Updates the search query state
        console.log("Search query:", searchQuery);
    };

    return (
        // form for user input, which turns into searchQuery
        <form onSubmit={handleSubmit}>
            <label>Semantic search: 
                <input 
                    type="text"
                    value={searchQuery}
                    onChange={(e) => {
                        setSearchQuery(e.target.value);
                    }} 
                />
            </label>
        </form>
    );
} 
