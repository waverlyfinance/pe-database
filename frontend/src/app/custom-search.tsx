import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import React, { useEffect, useState } from 'react';
import { Portco } from './data-table';
import { useRouter } from 'next/navigation';
import { usePerplexity } from '../contexts/perplexityContext';

interface CustomSearchProps {
    selectedRows: Portco[]; // selectedRows is an array of type Portco
}

const CustomSearch: React.FC<CustomSearchProps> = ({ selectedRows }) => {
    const [customQuery, setCustomQuery] = useState(""); // state to hold the query for the Perplexity search
    const router = useRouter(); // for page navigation
    const [PerplexityResponse, setPerplexityResponse] = useState("")

    // for async management. Navigate to search page once PerplexityResponse is populated
    useEffect(() => {
        if (PerplexityResponse.length > 0) {
            console.log("Navigating to search page with PerplexityResponse data: ", PerplexityResponse);
            // router.push('/search'); // navigate to search page
        }
    }, [PerplexityResponse, router]); 

    // Handler which is updated once the user clicks the button.   
    const handleButtonClick = async () => {
        console.log("Selected Rows: ", selectedRows)
        console.log("Query: ", customQuery)

        // Construct a query to be sent to the Perplexity API, for each selected row 
        let data: any = [];

        for (const row of selectedRows) {
            const query = `${customQuery} The company is: ${row.company_name} and the Private Equity firm that owns it is ${row.firm}. The investment was made in ${row.date_of_investment_stan}`
            console.log("Constructed query: ", query)
            const perplexityOutput = await callApi(query);
            
            // update empty array for each selected row
            data.push({
                company_name: row.company_name,
                firm: row.firm,
                date_of_investment: row.date_of_investment_stan,
                perplexityOutput
            });
            console.log("Data pushed:", data)
        }
        setPerplexityResponse(data); // set the context data
        console.log("Context set with data: ", data);
        console.log("Perplexity response after updated context: ", PerplexityResponse);
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