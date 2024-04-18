import React, { useState, useEffect } from "react";

export default function Search ({ onSearchChange }) {
    // set state
    const [searchQuery, setSearchQuery] = useState("");
    console.log(onSearchChange);

    const handleSubmit = (e) => {
        e.preventDefault(); // prevent the default form submit action, which refreshes the page
        onSearchChange(searchQuery); // passes the current state back to the Parent homepage
    };

    return (
        // form for user input, which turns into searchQuery
        <form onSubmit={handleSubmit}>
            <label>Semantic search for companies: 
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


// onSearchChange(e.target.value); //event handler, which feeds the value back to Homepage once the user types in the search bar



// const handleInputChange = (e) => {
//     setSearchQuery(e.target.value); // updates local state on each keystroke
// }
