
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { Runnable } from "@langchain/core/runnables";

export interface AIEngineConfig {
  readonly modelName: string;
  readonly temperature: number;
  readonly promptTemplate: string;
}

export enum CharacterComplexity {
  High = "HIGH_COMPLEXITY",
  Low = "LOW_COMPLEXITY",
  NotApplicable = "NOT_APPLICABLE",
}

class AIEngineError extends Error {
  constructor(message: string, options?: { cause: unknown }) {
    super(message, options);
    this.name = "AIEngineError";
  }
}

const getOpenAIApiKey = (): string => {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new AIEngineError(
      "AIEngine Initialization Failed: "OPENAI_API_KEY" is not set in the server environment."
    );
  }
  return apiKey;
};

class AIEngine {
  private static instance: AIEngine;
  private readonly llm: ChatOpenAI;
  private readonly conceptInferenceChain: Runnable<{ text: string }, string>;

  private static readonly CJK_UNICODE_BLOCK_THRESHOLD = 19968;

  private static readonly DEFAULT_CONFIG: AIEngineConfig = Object.freeze({
    modelName: "gpt-4-turbo",
    temperature: 0.1,
    promptTemplate: "Infer the single, primary concept from this text: "{text}"",
  });

  private constructor(config: AIEngineConfig) {
    try {
      const apiKey = getOpenAIApiKey();
      this.llm = new ChatOpenAI({
        apiKey,
        modelName: config.modelName,
        temperature: config.temperature,
      });

      const prompt = ChatPromptTemplate.fromTemplate(config.promptTemplate);
      const outputParser = new StringOutputParser();

      this.conceptInferenceChain = prompt.pipe(this.llm).pipe(outputParser);
    } catch (error) {
      throw new AIEngineError("AIEngine constructor failed", { cause: error });
    }
  }

  public static getInstance(config?: Partial<AIEngineConfig>): AIEngine {
    if (!AIEngine.instance) {
      const finalConfig = { ...AIEngine.DEFAULT_CONFIG, ...config };
      AIEngine.instance = new AIEngine(finalConfig);
    }
    return AIEngine.instance;
  }

  public async inferConcept(text: string): Promise<string | null> {
    if (!text?.trim()) {
      return null;
    }
    try {
      return await this.conceptInferenceChain.invoke({ text });
    } catch (error) {
      this.handleInferenceError(error, "inferConcept");
      return null;
    }
  }

  public static assessCharacterComplexity(text: string): CharacterComplexity {
    if (!text?.length) {
      return CharacterComplexity.NotApplicable;
    }

    const charCodeSum = Array.from(text).reduce(
      (sum, char) => sum + char.charCodeAt(0),
      0
    );

    const meanValue = charCodeSum / text.length;

    return meanValue > AIEngine.CJK_UNICODE_BLOCK_THRESHOLD
      ? CharacterComplexity.High
      : CharacterComplexity.Low;
  }

  private handleInferenceError(error: unknown, operationName: string): void {
    const engineError = new AIEngineError(
      "Operation '"operationName}' failed.",
      { cause: error }
    );
    console.error("[oriel AIEngine]: "engineError.message}, engineError.cause);
  }
}

export const aiEngine = AIEngine.getInstance();
"