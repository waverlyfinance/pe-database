import { usePerplexity } from '../src/contexts/perplexityContext';

const SearchPage = () => {
    const { PerplexityResponse, isLoading } = usePerplexity();
    console.log("Perplexity response: ", PerplexityResponse)

    return (
        <div>
            <h1>Search Results</h1>
            {isLoading ? <p>Loading...</p> : PerplexityResponse.map((item, index) => (
                <div key={index}>
                    <h2>{item.company_name}</h2>
                    <p>{item.firm}</p>
                    <p>{item.perplexityResponse}</p>
                </div>
            ))}
        </div>
    );
};

export default SearchPage;