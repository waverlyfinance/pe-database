// TODO: Fix date of investment
// TODO: Add field for PE firm 
// TODO: Fix encoding issues in raw HTML description

"use client";

import { useState, useEffect } from "react";
import Pagination from "./pagination";
import Filters from "./filters";

export default function Home() {
  // initial state setup
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(50);

  // Fetch the data
  useEffect(() => {
      fetch("/data.json")
        .then(response => response.json())
        .then(data => setData(data));
      
  }, []);
  
  // this second useEffect handles asynchronous nature of React. We want to wait until the initial data has been fetched before running     
  useEffect(() => {
    if (data.length > 0) {
      handleFilterChange({
        industry: undefined,
        region: undefined,
        fund: undefined,
        status: undefined,
    });
    console.log("Initial data:", data);
    }
  }, [data]);
    

  // Function to filter the data. Takes as input "filters". Returns a new array in which ONLY the industries returned are the desired filter. E.g. "Healthcare" 
  const handleFilterChange = (filters) => {
    console.log("Filters received", filters);

    const result = data.filter(company => {
      return (
        (!filters.industry || company.industry === filters.industry) &&
        (!filters.region || company.region === filters.region) &&
        (!filters.fund || company.fund === filters.fund) &&
        (!filters.status || company.status === filters.status)
      );
    });
    
    console.log("Filtered data:", result)
    setFilteredData(result);
  };

  // Show only 25 items per page
  const indexLast = currentPage * itemsPerPage; // 1*50 = 50
  const indexFirst = indexLast - itemsPerPage; // 50-50 = 0
  const visibleData = filteredData.slice(indexFirst, indexLast);
  
  const paginate = pageNumber => setCurrentPage(pageNumber); // change page function

  
  // html stuff
  return (
    <>
    
    {/* Filters content */}
    <div>
      <Filters data={data} onFilterChange={handleFilterChange} />
    </div>

    {/* Table content */}
    <div className="overflow-x-auto">
        <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
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
                <td className="px-6 py-4">{company.company_name}</td>
                <td className="px-6 py-4">{company.industry}</td>
                <td className="px-6 py-4">{company.region}</td>
                <td className="px-6 py-4">{company.fund}</td>
                <td className="px-6 py-4">{company.date_of_investment}</td>
                <td className="px-6 py-4">{company.company_description}</td>
                <td className="px-6 py-4">{company.status}</td>
                <td className="px-6 py-4"><a href={company.website}>website</a></td>
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
