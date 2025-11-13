import { Code2, Type, Hash, Calendar, Link as LinkIcon, List } from 'lucide-react';
import { generateId } from '../utils/helpers';

const TagPalette = ({ onDragStart }) => {
  const tagTemplates = [
    {
      name: 'text',
      icon: Type,
      description: 'Text content',
      color: 'bg-blue-100 border-blue-300',
      defaultConstraints: { type: 'string' },
    },
    {
      name: 'number',
      icon: Hash,
      description: 'Numeric value',
      color: 'bg-green-100 border-green-300',
      defaultConstraints: { type: 'number' },
    },
    {
      name: 'date',
      icon: Calendar,
      description: 'Date/timestamp',
      color: 'bg-purple-100 border-purple-300',
      defaultConstraints: { type: 'date' },
    },
    {
      name: 'url',
      icon: LinkIcon,
      description: 'URL/link',
      color: 'bg-orange-100 border-orange-300',
      defaultConstraints: { type: 'url' },
    },
    {
      name: 'list',
      icon: List,
      description: 'List of items',
      color: 'bg-pink-100 border-pink-300',
      defaultConstraints: { type: 'array' },
    },
    {
      name: 'custom',
      icon: Code2,
      description: 'Custom tag',
      color: 'bg-gray-100 border-gray-300',
      defaultConstraints: {},
    },
  ];

  const handleDragStart = (e, template) => {
    const newTag = {
      id: generateId(),
      name: template.name,
      constraints: template.defaultConstraints,
      attributes: {},
      children: [],
      expanded: true,
    };
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('application/json', JSON.stringify(newTag));
    if (onDragStart) {
      onDragStart(newTag);
    }
  };

  return (
    <div className="w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Tag Palette</h2>
      <p className="text-sm text-gray-600 mb-6">
        Drag tags to the canvas to build your XML pattern
      </p>

      <div className="space-y-3">
        {tagTemplates.map((template) => {
          const Icon = template.icon;
          return (
            <div
              key={template.name}
              draggable
              onDragStart={(e) => handleDragStart(e, template)}
              className={`${template.color} border-2 rounded-lg p-3 cursor-move hover:shadow-md transition-shadow`}
            >
              <div className="flex items-center space-x-3">
                <Icon size={20} className="text-gray-700" />
                <div>
                  <div className="font-mono font-semibold text-gray-900">
                    &lt;{template.name}&gt;
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    {template.description}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2">Tips</h3>
        <ul className="text-xs text-blue-800 space-y-2">
          <li>Drag tags to the canvas</li>
          <li>Drop tags on other tags to nest them</li>
          <li>Click the gear icon to configure constraints</li>
          <li>Use the preview to see the XML structure</li>
        </ul>
      </div>
    </div>
  );
};

export default TagPalette;
