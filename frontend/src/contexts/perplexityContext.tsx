import { createContext, useContext, useState, Dispatch, SetStateAction, ReactNode } from 'react';

interface PerplexityContextType {
    PerplexityResponse: any[];
    setPerplexityResponse: Dispatch<SetStateAction<any[]>>;
}

interface SearchProviderProps {
    children: ReactNode; // type that covers anything that can be rendered in a JSX expression
}

const PerplexityContext = createContext<PerplexityContextType>({
    PerplexityResponse: [],
    setPerplexityResponse: () => {}
});

export const SearchProvider: React.FC<SearchProviderProps> = ({ children }) => {
    const [PerplexityResponse, setPerplexityResponse] = useState<any[]>([]);
    return (
        <PerplexityContext.Provider value={{ PerplexityResponse, setPerplexityResponse }}>
            {children}
        </PerplexityContext.Provider>
    );
};

export const usePerplexity = () => {
    const context = useContext(PerplexityContext);
    return context
};