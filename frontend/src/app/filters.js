import React, { useState, useEffect } from "react";

// Component which takes in data (an array containing my JSON data), and onFilterChange
const Filters = ( {data, onFilterChange }) => {
    // define filters here
    const [selectedFirm, setSelectedFirm] = useState("");
    const [selectedIndustry, setSelectedIndustry] = useState("");
    const [selectedRegion, setSelectedRegion] = useState("");
    const [selectedFund, setSelectedFund] = useState("");
    const [selectedStatus, setSelectedStatus] = useState("");

    // function to generate an array of all the unique values for a given key. E.g. Industry, or Region
    const getUniqueValues = (key) => {
        let totalValues = data.map(company => company[key]) // new array, which is a subset of "data". Contains all the values for a given key. E.g. For "Industry" 
        let uniqueValues = [...new Set(totalValues)] // Set returns the unique values only. The [...] convention transforms the set back into an array, which we need
        return uniqueValues;
    };

    // when any filter changes (useEffect), call the onFilterChange function to update the state
    useEffect(() => {
        onFilterChange({
            firm: selectedFirm,
            industry: selectedIndustry,
            region: selectedRegion,
            fund: selectedFund,
            status_current: selectedStatus,
        });
    }, [selectedFirm, selectedIndustry, selectedRegion, selectedFund, selectedStatus]);

    return (
        <div>
            {/* Dropdown menu. Upon user selection, updates "selectedIndustry" to that value */}
            <select value={selectedFirm} onChange={e => setSelectedFirm(e.target.value)}> 
                <option value="">All Firms</option>
                {getUniqueValues("firm").map(firm => ( 
                    <option key={firm} value={firm}>{firm}</option> 
            ))}
            </select>

            <select value={selectedIndustry} onChange={e => setSelectedIndustry(e.target.value)}> 
                <option value="">All industries</option>
                {getUniqueValues("industry").map(industry => ( // Returns new array containing every unique value in "industry". New array contains the following JSX code
                    <option key={industry} value={industry}>{industry}</option> // e.g. option value="Healthcare", option value="Tech"
            ))}
            </select>

            <select value={selectedRegion} onChange={e => setSelectedRegion(e.target.value)}> 
                <option value="">All regions</option>
                {getUniqueValues("region").map(region => ( 
                    <option key={region} value={region}>{region}</option> 
            ))}
            </select>
            
            <select value={selectedFund} onChange={e => setSelectedFund(e.target.value)}> 
                <option value="">All funds</option>
                {getUniqueValues("fund").map(fund => ( 
                    <option key={fund} value={fund}>{fund}</option>
            ))}
            </select>

            <select value={selectedStatus} onChange={e => setSelectedStatus(e.target.value)}> 
                <option value="">All investments</option>
                {getUniqueValues("status_current").map(status_current => ( 
                    <option key={status_current} value={status_current}>{status_current}</option> 
            ))}
            </select>
        </div>
    )
};

export default Filters;