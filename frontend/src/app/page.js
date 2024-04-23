"use client";

import { useState, useEffect } from "react";
import Pagination from "./pagination";
import Filters from "./filters";
import Search from "./search";

// TODO: Fix date of investment
// TODO: Fix encoding issues in raw HTML description

export default function Home() {
  // data states
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [currentPage, setCurrentPage] = useState(1); // for pagination
  const [itemsPerPage] = useState(50);
  const [searchQuery, setSearchQuery] = useState(""); 

  // states to set up filters
  const [firm, setFirm] = useState(''); 
  const [industry, setIndustry] = useState('');
  const [region, setRegion] = useState('');
  const [status_current, setStatusCurrent] = useState('');

  // Fetch the data from Postgres database. Default is no filters 
  useEffect(() => {
    const fetchData = async () => {
        const params = new URLSearchParams({
          ...(firm && { firm }), // only returns if "firm" is truthy. E.g. Not undefined or empty
          ...(industry && { industry }),
          ...(region && { region }),
          ...(status_current && { status_current }), 
          ...(searchQuery && { searchQuery }),
        }).toString();
      
      console.log("parameters: ", params);
      
      const response = await fetch(`/api/data?${params}`);
      const data = await response.json();
      console.log("Fetched data: ", data); // to debug. Check what data is fetched from Postgres database
      setData(data);
      };  

      fetchData();  
  }, [searchQuery]); 
  
  // this second useEffect handles the async nature of React. We want to wait until the initial data has been fetched before running     
  useEffect(() => {
    if (data.length > 0) {
      handleFilterChange({});
    // console.log("Initial data:", data);
    }
  }, [data]);
    
  // Event handler to setFilteredData. Returns a new array in which ONLY the industries returned are the desired filter. E.g. "Healthcare" 
  const handleFilterChange = (filters) => {
    console.log("Filters received", filters);

    const result = data.filter(company => { // Returns an array, which is a subset of "data" array. Loops through "data" and only returns TRUE entries. E.g. industry = "Healthcare" 
      return (
        (!filters.firm || company.firm === filters.firm) &&
        (!filters.industry_stan || company.industry_stan === filters.industry_stan) &&
        (!filters.region_stan || company.region_stan === filters.region_stan) &&
        (!filters.fund || company.fund === filters.fund) &&
        (!filters.status_current_stan || company.status_current_stan === filters.status_current_stan)
      );
    });
    
    console.log("Filtered data:", result)
    setFilteredData(result);
  };


  // Show only 50 items per page
  const indexLast = currentPage * itemsPerPage; // 1*50 = 50
  const indexFirst = indexLast - itemsPerPage; // 50-50 = 0
  const visibleData = filteredData.slice(indexFirst, indexLast);
  
  const paginate = pageNumber => setCurrentPage(pageNumber); // change page function

  
  // html stuff
  return (
    <>
    <meta charSet="utf-8"/>
    
    {/* Semantic search */}
    <div>
      <Search onSearchChange={setSearchQuery} />
    </div>
    
    {/* Filters content */}
    <div>
      <Filters data={data} onFilterChange={handleFilterChange} />
    </div>

    {/* Table content */}
    <div className="overflow-x-auto">
        <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th scope="col" className="px-6 py-3">Firm</th>
              <th scope="col" className="px-6 py-3">Company</th>
              <th scope="col" className="px-6 py-3">Industry</th>
              <th scope="col" className="px-6 py-3">Region</th>
              <th scope="col" className="px-6 py-3">Fund</th>
              <th scope="col" className="px-6 py-3">Date of Investment</th>
              <th scope="col" className="px-6 py-3">Description</th>
              <th scope="col" className="px-6 py-3">Status</th>
              <th scope="col" className="px-6 py-3">Website</th>
            </tr>
          </thead>
          <tbody>
            {visibleData.map((company, index) => (
              <tr key ={index} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <td className="px-6 py-4">{company.firm}</td>
                <td className="px-6 py-4">{company.company_name}</td>
                <td className="px-6 py-4">{company.industry_stan}</td>
                <td className="px-6 py-4">{company.region_stan}</td>
                <td className="px-6 py-4">{company.fund}</td>
                <td className="px-6 py-4">{company.date_of_investment_stan}</td>
                <td className="px-6 py-4">{company.company_description}</td>
                <td className="px-6 py-4">{company.status_current_stan}</td>
                <td className="px-6 py-4"><a href={company.website}>link</a></td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination
          itemsPerPage={itemsPerPage}
          totalItems={filteredData.length}
          paginate={paginate}
        />
    </div>
    </>
  );
}
