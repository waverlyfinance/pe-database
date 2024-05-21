import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const SearchPage = () => {
    const router = useRouter();

    useEffect(() => {
        if (router.isReady && router.query && 'data' in router.query) {
            console.log("Router is ready:", router.isReady);
            console.log("Data from URL:", router.query.data);
        }
    }, [router.isReady, router.query]);

    // Wait until the data is available
    if (router.isReady) {
        // const { data } = router.query; // data is the string in the URL
        const dataString = router.query.data;
        try {
            const items = JSON.parse(dataString); 
            console.log("Loaded items:", items); 
        } catch (error) {
            console.error(error)
        }
        return (
            <div>
                <h1>Search Results</h1>
                {items && items.map((item, index) => (
                    <div key={index}>
                        <h2>{item.company_name}</h2>
                        <p>{item.firm}</p>
                        <p>{item.perplexityOutput}</p>
                    </div>
                ))}
            </div>
        );
    } else {
        return <div>Loading...</div>
    }
    };


export default SearchPage;
