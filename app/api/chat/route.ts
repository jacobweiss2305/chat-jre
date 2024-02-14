import { kv } from '@vercel/kv'
import { Message, OpenAIStream, StreamingTextResponse } from 'ai'
import OpenAI from 'openai'

import { auth } from '@/auth'
import { nanoid } from '@/lib/utils'

import { getContext } from '@/lib/context'

export const runtime = 'edge'

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
})

const companyName = process.env.COMPANY_NAME;

export async function POST(req: Request) {
    const json = await req.json()
    const { messages, previewToken } = json
    const userId = (await auth())?.user.id

    const lastMessage = messages[messages.length - 1]

    const transcript  = await getContext(lastMessage.content, 'youtube')

    const title_description  = await getContext(lastMessage.content, 'youtube', 3000, 0.7, false)

    const spotify_description = await getContext(lastMessage.content, 'spotify')

    const prompt = [
        {
            role: 'system',
        content: `You have been hired by ${companyName} podcast to be a helpful assistant.
        Help the user by answering their questions about ${companyName} podcast.
        Do not rely on prior knowledge, and only give your expertise if asked for.

        Use the podcast transcript and metadata to answer the user's questions.

        START SPOTIFY METADATA:
        ${spotify_description}
        END OF SPOTIFY METADATA

        START YOUTUBE METADATA:
        ${title_description}
        END OF YOUTUBE METADATA
    
        START YOUTUBE TRANSCRIPT:
        ${transcript}
        END OF YOUTUBE TRANSCRIPT

    `,
        },
    ]

    if (!userId) {
        return new Response('Unauthorized', {
            status: 401
        })
    }

    if (previewToken) {
        openai.apiKey = previewToken
    }

    const res = await openai.chat.completions.create({
        model: 'gpt-4-0125-preview',
        messages: [...prompt, ...messages.filter((message: Message) => message.role === 'user')],
        temperature: 0.7,
        stream: true
    })

    const stream = OpenAIStream(res, {
        async onCompletion(completion) {
            const title = json.messages[0].content.substring(0, 100)
            const id = json.id ?? nanoid()
            const createdAt = Date.now()
            const path = `/chat/${id}`
            const payload = {
                id,
                title,
                userId,
                createdAt,
                path,
                messages: [
                    ...messages,
                    {
                        content: completion,
                        role: 'assistant'
                    }
                ]
            }
            await kv.hmset(`chat:${id}`, payload)
            await kv.zadd(`user:chat:${userId}`, {
                score: createdAt,
                member: `chat:${id}`
            })
        }
    })

    return new StreamingTextResponse(stream)
}
