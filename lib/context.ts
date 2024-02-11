import { getMatchesFromEmbeddings } from "./pinecone";
import { getEmbeddings } from './embeddings'

export type Match = {
    id: string;
    score: number; // Reflecting that score can be undefined
    values: any[];
    sparseValues: any;
    metadata: {
        text: string;
    };
}

// The function `getContext` is used to retrieve the context of a given message
export const getContext = async (message: string, namespace: string, maxTokens = 3000, minScore = 0.7, getOnlyText = true): Promise<string> => {
    
    // Get the embeddings of the input message
    const embedding = await getEmbeddings(message);
    // Retrieve the matches for the embeddings from the specified namespace
    const matches = await getMatchesFromEmbeddings(embedding, 10, namespace);
    // Filter and extract as before
    const docs = matches.map(m => m.metadata?.text ?? "Unfortunately, no relevant context was found for this message.");

    let relevantContext = docs.join("\n");
    if (relevantContext.length > maxTokens) {
        relevantContext = relevantContext.substring(0, maxTokens);
    }

    return relevantContext;
}