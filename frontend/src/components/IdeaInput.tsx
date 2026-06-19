import { useState } from 'react';
import { Send, Loader2, Lightbulb } from 'lucide-react';

interface IdeaInputProps {
  onGenerate: (idea: string) => void;
  isGenerating: boolean;
  examples: string[];
}

export default function IdeaInput({ onGenerate, isGenerating, examples }: IdeaInputProps) {
  const [idea, setIdea] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (idea.trim() && !isGenerating) {
      onGenerate(idea.trim());
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="glass p-2 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-ignivox-400 ml-3 shrink-0" />
          <input
            type="text"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="Describe your startup idea... e.g., 'Build an AI platform for college students'"
            className="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-500 py-3 px-2"
            disabled={isGenerating}
          />
          <button
            type="submit"
            disabled={!idea.trim() || isGenerating}
            className="btn-primary flex items-center gap-2 shrink-0"
          >
            {isGenerating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            {isGenerating ? 'Generating...' : 'Generate Blueprint'}
          </button>
        </div>
      </form>
    </div>
  );
}
