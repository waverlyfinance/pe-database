import React, { useState, useEffect } from "react";
import { SelectFilter } from "../components/selectFilter";

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
        <div className="flex gap-2 items-center">
            {/* Dropdown menu. Upon user selection, updates "selectedFirm" to that value */}
            <SelectFilter
                uniqueValues={getUniqueValues("firm")}
                placeholder="All firms"
                selectedValue={selectedFirm}
                onValueChange={setSelectedFirm} // updates state once onValueChange is called
            />

            <SelectFilter
                uniqueValues={getUniqueValues("industry_stan")}
                placeholder="All industries"
                selectedValue={selectedIndustry}
                onValueChange={setSelectedIndustry} // updates state once onValueChange is called
            />
            
            <SelectFilter
                uniqueValues={getUniqueValues("region_stan")}
                placeholder="All regions"
                selectedValue={selectedRegion}
                onValueChange={setSelectedRegion} // updates state once onValueChange is called
            />
                        
            <SelectFilter
                uniqueValues={getUniqueValues("status_current_stan")}
                placeholder="All investments"
                selectedValue={selectedStatus}
                onValueChange={setSelectedStatus} // updates state once onValueChange is called
            />

            {/* Dropdown menu. Upon user selection, updates "selectedIndustry" to that value
            <select value={selectedFirm} onChange={e => setSelectedFirm(e.target.value)}> 
                <option value="">All Firms</option>
                {getUniqueValues("firm").map(firm => ( 
                    <option key={firm} value={firm}>{firm}</option> 
            ))}
            </select> */}
        </div>
    )
};

export default Filters;