'use client';

import { 
  FiBarChart2, 
  FiShare2, 
  FiSettings, 
  FiStar,
  FiFileText,
  FiHelpCircle,
  FiEdit3,
} from 'react-icons/fi';
import { BsQuestionCircle } from 'react-icons/bs';
import { HiOutlineDocumentText } from 'react-icons/hi';

interface StudioFeature {
  id: string;
  title: string;
  icon: React.ReactNode;
}

interface StudioGridProps {
  onToolSelect: (toolId: string | null) => void;
  activeTool: string | null;
}

export default function StudioGrid({ onToolSelect, activeTool }: StudioGridProps) {
  const features: StudioFeature[] = [
    {
      id: 'outline',
      title: 'Outline',
      icon: <HiOutlineDocumentText className="w-6 h-6" />,
    },
    {
      id: 'summarize',
      title: 'Summarize',
      icon: <FiFileText className="w-6 h-6" />,
    },
    {
      id: 'faq',
      title: 'FAQ',
      icon: <FiHelpCircle className="w-6 h-6" />,
    },
    {
      id: 'quiz',
      title: 'Quiz',
      icon: <BsQuestionCircle className="w-6 h-6" />,
    },
    {
      id: 'flashcards',
      title: 'Flashcards',
      icon: <FiFileText className="w-6 h-6" />,
    },
    {
      id: 'query',
      title: 'Query',
      icon: <FiHelpCircle className="w-6 h-6" />,
    },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-200">Studio</h2>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <button className="text-gray-400 hover:text-gray-200 transition-colors">Analytics</button>
          <button className="text-gray-400 hover:text-gray-200 transition-colors">Share</button>
          <button className="text-gray-400 hover:text-gray-200 transition-colors flex items-center gap-1">
            <FiSettings className="w-4 h-4" />
            Settings
          </button>
          <button className="px-3 py-1 text-xs bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors flex items-center gap-1">
            <FiStar className="w-3 h-3" />
            PRO
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Language Selection Box - Placeholder */}
        <div 
          className="border border-emerald-600/30 rounded-lg p-4 bg-emerald-900/10 cursor-not-allowed opacity-50"
          title="Audio Overview - Coming soon"
        >
          <p className="text-sm text-gray-300 mb-3">Create an Audio Overview in:</p>
          <div className="flex flex-wrap gap-2">
            {['हिन्दी', 'বাংলা', 'ગુજરાતી', 'ಕನ್ನಡ', 'മലയാളം', 'मराठी', 'ਪੰਜਾਬੀ', 'தமிழ்', 'తెలుగు'].map((lang) => (
              <span key={lang} className="text-xs text-gray-400">{lang}</span>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2 italic">Coming soon</p>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-2 gap-3">
          {features.map((feature) => (
            <button
              key={feature.id}
              onClick={() => onToolSelect(activeTool === feature.id ? null : feature.id)}
              className={`group relative rounded-lg border p-4 transition-all ${
                activeTool === feature.id
                  ? 'border-emerald-500 bg-emerald-900/20'
                  : 'border-gray-700 bg-gray-800/50 hover:border-gray-600 hover:bg-gray-800'
              }`}
            >
              <div className="flex flex-col items-center text-center gap-2">
                <div className={`transition-colors ${
                  activeTool === feature.id ? 'text-emerald-400' : 'text-gray-400 group-hover:text-gray-300'
                }`}>
                  {feature.icon}
                </div>
                <h3 className={`text-sm font-medium transition-colors ${
                  activeTool === feature.id ? 'text-emerald-300' : 'text-gray-300 group-hover:text-gray-200'
                }`}>
                  {feature.title}
                </h3>
              </div>
            </button>
          ))}
        </div>

        {/* Instructions */}
        <p className="text-xs text-gray-500 leading-relaxed">
          Studio output will be saved here. After adding sources, click to add Audio Overview, Study Guide, Mind Map, and more!
        </p>
      </div>

      {/* Add Note Button */}
      <div className="p-6 border-t border-gray-800">
        <button className="w-full px-4 py-3 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors flex items-center justify-center gap-2 font-medium">
          <FiEdit3 className="w-4 h-4" />
          Add note
        </button>
      </div>
    </div>
  );
}
