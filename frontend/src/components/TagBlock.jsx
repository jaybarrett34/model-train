import { useState } from 'react';
import { Draggable } from '@hello-pangea/dnd';
import { ChevronRight, ChevronDown, Edit2, Trash2, Settings } from 'lucide-react';
import clsx from 'clsx';

const TagBlock = ({ tag, index, onEdit, onDelete, onToggleExpanded, level = 0 }) => {
  const [showMenu, setShowMenu] = useState(false);

  const hasChildren = tag.children && tag.children.length > 0;
  const hasConstraints = tag.constraints && Object.keys(tag.constraints).length > 0;

  return (
    <Draggable draggableId={tag.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className="mb-2"
          style={{
            ...provided.draggableProps.style,
            marginLeft: `${level * 24}px`,
          }}
        >
          <div
            className={clsx(
              'tag-block flex items-center justify-between',
              snapshot.isDragging && 'tag-block-dragging shadow-lg'
            )}
            onMouseEnter={() => setShowMenu(true)}
            onMouseLeave={() => setShowMenu(false)}
          >
            <div className="flex items-center space-x-2 flex-1">
              {hasChildren && (
                <button
                  onClick={() => onToggleExpanded(tag.id)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  {tag.expanded ? (
                    <ChevronDown size={16} />
                  ) : (
                    <ChevronRight size={16} />
                  )}
                </button>
              )}

              <div className="flex items-center space-x-2">
                <span className="font-mono font-semibold text-primary-700">
                  &lt;{tag.name}&gt;
                </span>

                {hasConstraints && (
                  <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                    {Object.keys(tag.constraints).length} constraints
                  </span>
                )}

                {tag.attributes && Object.keys(tag.attributes).length > 0 && (
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                    {Object.keys(tag.attributes).length} attrs
                  </span>
                )}
              </div>
            </div>

            {showMenu && (
              <div className="flex space-x-1">
                <button
                  onClick={() => onEdit(tag)}
                  className="p-2 hover:bg-primary-100 rounded transition-colors"
                  title="Configure tag"
                >
                  <Settings size={16} className="text-primary-600" />
                </button>
                <button
                  onClick={() => onEdit(tag)}
                  className="p-2 hover:bg-gray-100 rounded transition-colors"
                  title="Edit"
                >
                  <Edit2 size={16} className="text-gray-600" />
                </button>
                <button
                  onClick={() => onDelete(tag.id)}
                  className="p-2 hover:bg-red-100 rounded transition-colors"
                  title="Delete"
                >
                  <Trash2 size={16} className="text-red-600" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </Draggable>
  );
};

export default TagBlock;
