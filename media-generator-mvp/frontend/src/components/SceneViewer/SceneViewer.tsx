import React from 'react';
import { motion } from 'framer-motion';
import { Scene } from '../../types';
import { 
  Users, 
  MapPin, 
  Heart, 
  Activity, 
  BookOpen,
  Palette,
  Eye
} from 'lucide-react';

interface SceneViewerProps {
  scenes: Scene[];
  title?: string;
}

const SceneViewer: React.FC<SceneViewerProps> = ({ scenes, title = "Scene Estratte" }) => {
  if (!scenes || scenes.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <BookOpen className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-600">Nessuna scena disponibile</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 mb-4">
        <Eye className="w-5 h-5 text-primary-600" />
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded-full text-sm font-medium">
          {scenes.length} scene{scenes.length !== 1 ? '' : 'a'}
        </span>
      </div>

      <div className="grid gap-4">
        {scenes.map((scene, index) => (
          <motion.div
            key={scene.id || index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-900">
                {scene.title || `Scena ${index + 1}`}
              </h4>
              <div className="flex items-center space-x-1">
                <Palette className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-500 capitalize">
                  {scene.mood || 'Non specificato'}
                </span>
              </div>
            </div>

            {/* Contenuto della scena */}
            {scene.content && (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-700 leading-relaxed italic">
                  "{scene.content}"
                </p>
              </div>
            )}

            {/* Summary */}
            {scene.summary && (
              <div className="mb-4">
                <div className="flex items-center space-x-2 mb-1">
                  <BookOpen className="w-4 h-4 text-indigo-500" />
                  <span className="text-sm font-medium text-gray-700">Riassunto</span>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {scene.summary}
                </p>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-4">
              {/* Colonna sinistra */}
              <div className="space-y-3">
                {scene.characters && scene.characters.length > 0 && (
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <Users className="w-4 h-4 text-blue-500" />
                      <span className="text-sm font-medium text-gray-700">Personaggi</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {scene.characters.map((character, i) => (
                        <span
                          key={i}
                          className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
                        >
                          {character}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {scene.setting && (
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <MapPin className="w-4 h-4 text-green-500" />
                      <span className="text-sm font-medium text-gray-700">Ambientazione</span>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {scene.setting}
                    </p>
                  </div>
                )}
              </div>

              {/* Colonna destra */}
              <div className="space-y-3">
                {scene.themes && scene.themes.length > 0 && (
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <Activity className="w-4 h-4 text-purple-500" />
                      <span className="text-sm font-medium text-gray-700">Temi</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {scene.themes.map((theme, i) => (
                        <span
                          key={i}
                          className="inline-block bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full"
                        >
                          {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {scene.mood && (
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <Heart className="w-4 h-4 text-red-500" />
                      <span className="text-sm font-medium text-gray-700">Mood/Atmosfera</span>
                    </div>
                    <span className="inline-block bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                      {scene.mood}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Immagine generata */}
            {scene.image_url && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Palette className="w-4 h-4 text-orange-500" />
                  <span className="text-sm font-medium text-gray-700">Immagine Generata</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    scene.image_generation_status === 'completed' ? 'bg-green-100 text-green-700' :
                    scene.image_generation_status === 'processing' ? 'bg-yellow-100 text-yellow-700' :
                    scene.image_generation_status === 'failed' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {scene.image_generation_status === 'completed' ? 'Completata' :
                     scene.image_generation_status === 'processing' ? 'In elaborazione' :
                     scene.image_generation_status === 'failed' ? 'Errore' : 'In attesa'}
                  </span>
                </div>
                <div className="bg-gray-100 rounded-lg p-2">
                  <img 
                    src={scene.image_url} 
                    alt={`Immagine per ${scene.title}`}
                    className="w-full h-32 object-cover rounded"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>  );
};

export default SceneViewer;
