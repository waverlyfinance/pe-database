"use client";

import { useState, useEffect } from "react";
import Filters from "./filters";
import { SearchBar } from "@/app/searchBar";
import { DataTable, Portco, columns } from "./data-table";
import CustomSearch from "./custom-search";

export default function Home() {
  // states related to the core database + semantic search
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [searchQuery, setSearchQuery] = useState(""); 

  // states to set up filters
  const [firm, setFirm] = useState("");
  const [industry_stan, setIndustry] = useState("");
  const [region_stan, setRegion] = useState("");
  const [status_current_stan, setStatus] = useState(""); 

  // states for the custom Perplexity search
  const [selectedRows, setSelectedRows] = useState([]);


  // Fetch the data from Postgres database. Default is no filters 
  useEffect(() => {
    const fetchData = async () => {
      const params = new URLSearchParams({
        ...(firm && { firm }), // only returns if "firm" is truthy. E.g. Not undefined or empty
        ...(industry_stan && { industry_stan }),
        ...(region_stan && { region_stan }),
        ...(status_current_stan && { status_current_stan }), 
        ...(searchQuery && { searchQuery }), 
      }).toString();
    
      console.log("parameters: ", params);
      
      const response = await fetch(`/api/data?${params}`);
      const data = await response.json();
      console.log("Fetched data: ", data); // to debug. Check what data is fetched from Postgres database
      setData(data);
      console.log("industry: ", industry_stan, "region: ", region_stan, "status: ", status_current_stan);  
    };  
      
      fetchData()

  }, [searchQuery]); 
  
  // this second useEffect handles the async nature of React. We want to wait until the initial data has been fetched before running     
  useEffect(() => {
    if (data.length > 0) {
      handleFilterChange({});
    }
  }, [data]);
    
  // Event handler to setFilteredData. Returns a new array in which ONLY the industries returned are the desired filter. E.g. "Healthcare" 
  const handleFilterChange = (filters) => {
    console.log("Filters received", filters);
    setFirm(filters.firm);
    setIndustry(filters.industry_stan);
    setRegion(filters.region_stan);
    setStatus(filters.status_current_stan);

    const result = data.filter(company => { // Returns an array, which is a subset of "data" array. Loops through "data" and only returns TRUE entries. E.g. industry = "Healthcare" 
      return (
        (!filters.firm || company.firm === filters.firm) &&
        (!filters.industry_stan || company.industry_stan === filters.industry_stan) &&
        (!filters.region_stan || company.region_stan === filters.region_stan) &&
        (!filters.status_current_stan || company.status_current_stan === filters.status_current_stan)
      );
    });
    
    console.log("Filtered data:", result)
    setFilteredData(result);
  };

  // Event handler for changes in selected rows. Pass the local data from the Data Table component to homepage, which then gets passed to the Custom Search component
  const handleSelectedRows = (rows) => {
    setSelectedRows(rows);
  }
  
  // JSX content
  return (
    <>
    <meta charSet="utf-8"/>
    
    {/* Header */}
    <div className="flex flex-col gap-2 p-4 py-2">
      {/* Filters content */}
      <div>
        <Filters data={data} onFilterChange={handleFilterChange} />
      </div>

      {/* Semantic search using ShadCN */}
      <div className="max-w-lg py-2">
        <SearchBar searchQuery={searchQuery} onSearchChange={setSearchQuery}/> 
      </div>

      {/* Perplexity custom query */}
      <div className="flex items-center space-x-4 py-2 max-w-4xl">
        <CustomSearch selectedRows={selectedRows} />
      </div>
    </div> 


    {/* Table content using ShadCN */}
    <div className="container mx-auto my-10 p-4">
      <DataTable columns={columns} data={filteredData} onSelectedRowsChange={handleSelectedRows} />
    </div>
    </>
  );
}
