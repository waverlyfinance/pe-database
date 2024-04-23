import React, { useState, useEffect } from "react";

// Component which takes in data (an array containing my JSON data), and onFilterChange
const Filters = ( {data, onFilterChange }) => {
    // define filters here
    const [selectedFirm, setSelectedFirm] = useState("");
    const [selectedIndustry, setSelectedIndustry] = useState("");
    const [selectedRegion, setSelectedRegion] = useState("");
    // const [selectedFund, setSelectedFund] = useState("");
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
            industry_stan: selectedIndustry,
            region_stan: selectedRegion,
            // fund: selectedFund,
            status_current_stan: selectedStatus,
        });
    }, [selectedFirm, selectedIndustry, selectedRegion, selectedStatus]);

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
                {getUniqueValues("industry_stan").map(industry_stan => ( // Returns new array containing every unique value in "industry". New array contains the following JSX code
                    <option key={industry_stan} value={industry_stan}>{industry_stan}</option> // e.g. option value="Healthcare", option value="Tech"
            ))}
            </select>

            <select value={selectedRegion} onChange={e => setSelectedRegion(e.target.value)}> 
                <option value="">All regions</option>
                {getUniqueValues("region_stan").map(region_stan => ( 
                    <option key={region_stan} value={region_stan}>{region_stan}</option> 
            ))}
            </select>
            
            {/* <select value={selectedFund} onChange={e => setSelectedFund(e.target.value)}> 
                <option value="">All funds</option>
                {getUniqueValues("fund").map(fund => ( 
                    <option key={fund} value={fund}>{fund}</option>
            ))}
            </select> */}

            <select value={selectedStatus} onChange={e => setSelectedStatus(e.target.value)}> 
                <option value="">All investments</option>
                {getUniqueValues("status_current_stan").map(status_current_stan => ( 
                    <option key={status_current_stan} value={status_current_stan}>{status_current_stan}</option> 
            ))}
            </select>
        </div>
    )
};

export default Filters;