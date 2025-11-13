import { useState, useEffect } from 'react';
import { DragDropContext, Droppable } from '@hello-pangea/dnd';
import { Eye, Save, Code, Download } from 'lucide-react';
import TagPalette from '../components/TagPalette';
import TagBlock from '../components/TagBlock';
import ConstraintEditor from '../components/ConstraintEditor';
import useStore from '../store/useStore';
import { patternsApi } from '../services/api';
import { patternToXml, generateId } from '../utils/helpers';

const XMLEditor = () => {
  const { currentProject, xmlPattern, setXmlPattern, addTag, updateTag, removeTag } = useStore();
  const [tags, setTags] = useState([]);
  const [selectedTag, setSelectedTag] = useState(null);
  const [showConstraintEditor, setShowConstraintEditor] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [draggedTag, setDraggedTag] = useState(null);

  useEffect(() => {
    if (currentProject) {
      loadPattern();
    }
  }, [currentProject]);

  const loadPattern = async () => {
    if (!currentProject) return;

    try {
      const response = await patternsApi.get(currentProject.id);
      if (response.data.tags) {
        setTags(response.data.tags);
      }
    } catch (error) {
      console.error('Failed to load pattern:', error);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const data = e.dataTransfer.getData('application/json');
    if (data) {
      const newTag = JSON.parse(data);
      setTags([...tags, newTag]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(tags);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setTags(items);
  };

  const handleEditTag = (tag) => {
    setSelectedTag(tag);
    setShowConstraintEditor(true);
  };

  const handleSaveTag = (editedTag) => {
    setTags(tags.map(t => t.id === editedTag.id ? editedTag : t));
    setShowConstraintEditor(false);
    setSelectedTag(null);
  };

  const handleDeleteTag = (tagId) => {
    if (confirm('Are you sure you want to delete this tag?')) {
      setTags(tags.filter(t => t.id !== tagId));
    }
  };

  const handleToggleExpanded = (tagId) => {
    setTags(tags.map(t =>
      t.id === tagId ? { ...t, expanded: !t.expanded } : t
    ));
  };

  const handleSavePattern = async () => {
    if (!currentProject) {
      alert('Please select a project first');
      return;
    }

    try {
      await patternsApi.save(currentProject.id, { tags });
      alert('Pattern saved successfully!');
    } catch (error) {
      console.error('Failed to save pattern:', error);
      alert('Failed to save pattern');
    }
  };

  const handleExportXML = () => {
    if (tags.length === 0) {
      alert('No tags to export');
      return;
    }

    const xml = tags.map(tag => patternToXml([tag], tag.id)).join('\n\n');
    const blob = new Blob([xml], { type: 'text/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pattern.xml';
    a.click();
    URL.revokeObjectURL(url);
  };

  const generatePreview = () => {
    if (tags.length === 0) return '<empty pattern>';
    return tags.map(tag => patternToXml([tag], tag.id)).join('\n\n');
  };

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Code size={64} className="mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Project Selected</h2>
          <p className="text-gray-600">Please select or create a project to start editing XML patterns</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">XML Pattern Editor</h1>
            <p className="text-gray-600 mt-2">
              Design your data structure using drag-and-drop
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="btn-secondary flex items-center space-x-2"
            >
              <Eye size={20} />
              <span>{showPreview ? 'Hide' : 'Show'} Preview</span>
            </button>
            <button
              onClick={handleExportXML}
              className="btn-secondary flex items-center space-x-2"
            >
              <Download size={20} />
              <span>Export</span>
            </button>
            <button
              onClick={handleSavePattern}
              className="btn-primary flex items-center space-x-2"
            >
              <Save size={20} />
              <span>Save Pattern</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Editor Area */}
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Tag Palette - Left Sidebar */}
        <TagPalette onDragStart={setDraggedTag} />

        {/* Canvas - Center */}
        <div className="flex-1 bg-white rounded-lg shadow-md p-6 overflow-y-auto">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Canvas</h2>

          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="canvas">
              {(provided, snapshot) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  className={`drop-zone ${snapshot.isDraggingOver ? 'drop-zone-active' : ''}`}
                >
                  {tags.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-gray-400">
                      <div className="text-center">
                        <Code size={48} className="mx-auto mb-4" />
                        <p className="text-lg">Drag tags from the palette to start building</p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {tags.map((tag, index) => (
                        <TagBlock
                          key={tag.id}
                          tag={tag}
                          index={index}
                          onEdit={handleEditTag}
                          onDelete={handleDeleteTag}
                          onToggleExpanded={handleToggleExpanded}
                        />
                      ))}
                    </div>
                  )}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div>

        {/* Preview - Right Sidebar */}
        {showPreview && (
          <div className="w-96 bg-white rounded-lg shadow-md p-6 overflow-y-auto">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">XML Preview</h2>
            <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm font-mono overflow-x-auto">
              {generatePreview()}
            </pre>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Pattern Info</h3>
              <div className="text-sm text-blue-800 space-y-1">
                <div>Tags: {tags.length}</div>
                <div>
                  Constraints: {tags.reduce((sum, tag) =>
                    sum + Object.keys(tag.constraints || {}).length, 0
                  )}
                </div>
                <div>
                  Attributes: {tags.reduce((sum, tag) =>
                    sum + Object.keys(tag.attributes || {}).length, 0
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Constraint Editor Modal */}
      {showConstraintEditor && selectedTag && (
        <ConstraintEditor
          tag={selectedTag}
          onSave={handleSaveTag}
          onClose={() => {
            setShowConstraintEditor(false);
            setSelectedTag(null);
          }}
        />
      )}
    </div>
  );
};

export default XMLEditor;
