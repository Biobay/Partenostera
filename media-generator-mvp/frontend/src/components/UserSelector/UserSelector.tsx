import React, { useState, useEffect } from 'react';
import { User, Video, Zap, ArrowRight } from 'lucide-react';
import { User as UserType } from '../../types';
import { motion } from 'framer-motion';

interface UserSelectorProps {
  onUserSelect: (user: UserType) => void;
}

const UserSelector: React.FC<UserSelectorProps> = ({ onUserSelect }) => {
  const [users, setUsers] = useState<UserType[]>([]);

  useEffect(() => {
    // Carica utenti mock
    const mockUsers: UserType[] = [
      {
        id: '1',
        name: 'Marco Rossi',
        email: 'marco.rossi@example.com',
        type: 'image_editor',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Marco'
      },
      {
        id: '2',
        name: 'Elena Bianchi', 
        email: 'elena.bianchi@example.com',
        type: 'veo_user',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Elena'
      }
    ];
    setUsers(mockUsers);
    localStorage.setItem('mockUsers', JSON.stringify(mockUsers));
  }, []);

  const getUserDescription = (type: string) => {
    return type === 'veo_user' 
      ? 'Utilizza Veo2/3 per la generazione avanzata di video AI'
      : 'Sfrutta strumenti di generazione immagini e editor video tradizionali';
  };

  const getUserIcon = (type: string) => {
    return type === 'veo_user' ? Video : Zap;
  };

  const getUserTypeLabel = (type: string) => {
    return type === 'veo_user' ? 'Veo User' : 'Image Editor';
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.3,
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      <motion.div 
        className="max-w-4xl w-full"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div 
          className="text-center mb-12"
          variants={itemVariants}
        >
          <div className="flex items-center justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl flex items-center justify-center shadow-lg">
              <Video className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Media Generator MVP
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Genera contenuti multimediali da testo utilizzando intelligenza artificiale avanzata
          </p>
        </motion.div>

        {/* User Selection */}
        <motion.div variants={itemVariants}>
          <h2 className="text-2xl font-semibold text-gray-900 text-center mb-8">
            Seleziona il tuo profilo utente
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {users.map((user) => {
              const IconComponent = getUserIcon(user.type);
              return (
                <motion.div
                  key={user.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="group cursor-pointer"
                  onClick={() => onUserSelect(user)}
                >
                  <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-all duration-300 hover:border-primary-300">
                    {/* User Avatar & Info */}
                    <div className="flex items-center space-x-4 mb-6">
                      <div className="relative">
                        {user.avatar ? (
                          <img
                            src={user.avatar}
                            alt={user.name}
                            className="w-16 h-16 rounded-full border-2 border-gray-200"
                          />
                        ) : (
                          <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                            <User className="w-8 h-8 text-gray-500" />
                          </div>
                        )}
                        <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center shadow-lg">
                          <IconComponent className="w-4 h-4 text-white" />
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">
                          {user.name}
                        </h3>
                        <p className="text-sm text-gray-500">{user.email}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <IconComponent className="w-4 h-4 text-primary-600" />
                          <span className="text-sm font-medium text-primary-600">
                            {getUserTypeLabel(user.type)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-gray-600 mb-6 leading-relaxed">
                      {getUserDescription(user.type)}
                    </p>

                    {/* Features */}
                    <div className="space-y-3 mb-6">
                      {user.type === 'veo_user' ? (
                        <>
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            <span className="text-sm text-gray-700">Generazione video con Veo2/3</span>
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            <span className="text-sm text-gray-700">AI avanzata per contenuti complessi</span>
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            <span className="text-sm text-gray-700">Controllo qualità automatico</span>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            <span className="text-sm text-gray-700">Generazione immagini sequenziali</span>
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            <span className="text-sm text-gray-700">Editor video integrato</span>
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            <span className="text-sm text-gray-700">Validatori e guardrail</span>
                          </div>
                        </>
                      )}
                    </div>

                    {/* CTA Button */}
                    <button className="w-full btn-primary flex items-center justify-center space-x-2 group-hover:bg-primary-700 transition-colors">
                      <span>Inizia con {user.name}</span>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Footer Info */}
        <motion.div 
          className="text-center mt-12 text-gray-500"
          variants={itemVariants}
        >
          <p className="text-sm">
            Puoi cambiare utente in qualsiasi momento dalle impostazioni
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default UserSelector;