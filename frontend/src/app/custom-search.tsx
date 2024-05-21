import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import React, { useEffect, useState } from 'react';
import { Portco } from './data-table';
import { useRouter } from 'next/navigation';


interface CustomSearchProps {
    selectedRows: Portco[]; // selectedRows is an array of type Portco
    onPopoverTrigger:(show: boolean) => void;
    onPopoverData: (data: PerplexityDataType[]) => void; // function to pass data (of type defined below) 
}

export interface PerplexityDataType {
    company_name: string;
    firm: string;
    date_of_investment: number;
    perplexityOutput: string;
}

const CustomSearch: React.FC<CustomSearchProps> = ({ selectedRows, onPopoverTrigger, onPopoverData }) => {
    const [customQuery, setCustomQuery] = useState(""); // state to hold the query for the Perplexity search
    const router = useRouter(); // for page navigation

    // Handler which is updated once the user clicks the button.   
    const handleButtonClick = async () => {
        console.log("Selected Rows: ", selectedRows)
        console.log("Query: ", customQuery)

        // Construct a query to be sent to the Perplexity API, for each selected row 
        let data: any = [];

        for (const row of selectedRows) {
            const query = `The company we're interested in is ${row.company_name}, which is owned by the Private Equity firm ${row.firm}. The investment was made in ${row.date_of_investment_stan}. Based on this context, answer the following question: ${customQuery}`
            console.log("Constructed query: ", query)
            const perplexityOutput = await callApi(query);
            
            // update data for each selected row
            await data.push({
                company_name: row.company_name,
                firm: row.firm,
                date_of_investment: row.date_of_investment_stan,
                perplexityOutput
            });
            console.log("Data pushed:", data)
        }
        
        // When ready to navigate to new page
        console.log("Context set with data: ", data);
        // console.log("Perplexity response after updated context: ", PerplexityResponse);
    
        // Pass data onto popover, which will then display subsequent data
        onPopoverTrigger(true); // triggers the popover to show on the homepage
        onPopoverData(data);  

    
    };

    // Function to send Perplexity API request
    const callApi = async (query: string) => {
        try {
            const response = await fetch('/api/perplexity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });
            const data = await response.json();
            const output = data.response.data.choices[0].message.content;
            console.log('LLM answer: ', output)
            return output;
            
        } catch (error) {
            console.error('Error sending API request:', error);
        }
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
};

export default CustomSearch