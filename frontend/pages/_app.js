import { SearchProvider } from '../src/contexts/perplexityContext';

function MyApp({ Component, pageProps }) {
    return (
        <SearchProvider>
            <Component {...pageProps} />
        </SearchProvider>
    );
}

export default MyApp;