import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import React, { useState } from 'react';
import { Portco } from './data-table';

interface CustomSearchProps {
    selectedRows: Portco[]; // selectedRows is an array of type Portco
}

const CustomSearch: React.FC<CustomSearchProps> = ({ selectedRows }) => {
  const [customQuery, setCustomQuery] = useState(""); // state to hold the query for the Perplexity search

  // Function to handle once the user clicks the button.   
  const handleButtonClick = () => {
    const selectedData = selectedRows.map(row => ({
        company_name: row.company_name,
        firm: row.firm
    }));
    console.log("Selected Rows: ", selectedData)
    console.log("Query: ", customQuery)
    // Define subsequent API call here
  };
  
  return (
    <>
    <div className="flex-grow">
        <Input 
            placeholder="E.g. Does the founder still maintain partial ownership? Make sure to select companies first" 
            onChange={(e) => setCustomQuery(e.target.value)}
        />
    </div>

    <div>
        <Button 
        onClick={handleButtonClick} 
        disabled={selectedRows.length === 0}
        >
            Perform custom Google search
        </Button>
    </div>
    </>
  );
}

export default CustomSearch