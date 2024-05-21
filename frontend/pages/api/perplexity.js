import sdk from '@api/pplx';

export default async function Perplexity(req, res) {
    if (req.method !== 'POST') {
        res.setHeader('Allow', ['POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
        
    const { query } = req.body;
    const perplexityApiKey = process.env.PERPLEXITY_API_KEY;

    if (!perplexityApiKey) {
        return res.status(500).json({ error: 'API key is not defined' });
    }

    sdk.auth(perplexityApiKey);
    try {
        const response = await sdk.post_chat_completions({
        model: 'llama-3-70b-instruct',
        messages: [
            {role: 'system', content: `You are an artificial intelligence assistant and you need to engage in a helpful, polite conversation with a user.
            Do not be verbose. Do not provide explanations beyond what the user asks for. For example, do not lecture on how the Private Equity industry works.
            Provide citations whenever you state facts. In this case, you will need to cite the news article that you got the information from.
            For the sources: Use official press releases whenever possible. Avoid news articles unless you cannot find relevant press releases. 
            Find the top 5 sources. Then within the sources, leverage the most relevant one or two to generate your answer. Most sources will be lower quality.  
            * Use end footnote citations containing the url of the source in the following style [citation: url]. Output the citation as a seperate markdown paragraph at the end of your response
            * For example, a reference from "https://www.exac.com/exactech-announces-completion-of-merger-with-tpg-capital/" would be [citation|https://www.exac.com/exactech-announces-completion-of-merger-with-tpg-capital/]
            * Do NOT forget to provide the citations. You must never provide an answer without citations. If there are none, just say so.
            * Do NOT make up a citation. Output the URL link to the actual website that you got the information from.`},
            {role: 'user', content: query}
        ]
    });
    
    res.status(200).json({ response });
    return response
} catch (err) {
    console.error("API error:", err);
    res.status(500).json({ error: err.message });
}
}