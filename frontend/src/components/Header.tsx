import { Zap } from 'lucide-react';

interface HeaderProps {
  nvidiaMode: boolean;
}

export default function Header({ nvidiaMode }: HeaderProps) {
  return (
    <header className="border-b border-white/5 bg-surface/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-ignivox-500 to-emerald-600 flex items-center justify-center font-bold text-lg">
            I
          </div>
          <div>
            <span className="font-bold text-lg">Ignivox AI</span>
            <span className="hidden sm:inline text-xs text-gray-500 ml-2">Autonomous Co-Founder</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
            nvidiaMode ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'
          }`}>
            <Zap className="w-3 h-3" />
            {nvidiaMode ? 'NVIDIA NIM Active' : 'Demo Mode'}
          </div>
          <div className="hidden md:flex items-center gap-2 text-xs text-gray-500">
            <span className="px-2 py-1 rounded bg-white/5">NeMo</span>
            <span className="px-2 py-1 rounded bg-white/5">NIM</span>
            <span className="px-2 py-1 rounded bg-white/5">Retriever</span>
            <span className="px-2 py-1 rounded bg-white/5">Guardrails</span>
          </div>
        </div>
      </div>
    </header>
  );
}
