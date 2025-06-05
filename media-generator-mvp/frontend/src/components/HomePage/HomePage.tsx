import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  BookOpen, 
  FileText, 
  Zap, 
  Video,
  Image,
  Music,
  ArrowRight,
  Sparkles,
  Clock
} from 'lucide-react';
import { motion } from 'framer-motion';
import { User } from '../../types';
import FileUpload from '../FileUpload/FileUpload';

interface HomePageProps {
  user: User;
}

const HomePage: React.FC<HomePageProps> = ({ user }) => {
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(false);

  const features = [
    {
      icon: Image,
      title: 'Generazione Immagini',
      description: 'Crea immagini sequenziali correlate dal tuo testo',
      color: 'bg-blue-500'
    },
    {
      icon: Music,
      title: 'Audio Sincronizzato',
      description: 'Genera narrazione audio perfettamente allineata',
      color: 'bg-green-500'
    },
    {
      icon: Video,
      title: 'Video Finali',
      description: 'Combina tutto in video professionali MP4',
      color: 'bg-purple-500'
    },
    {
      icon: Sparkles,
      title: 'Validazione AI',
      description: 'Controlli qualità automatici e guardrail',
      color: 'bg-orange-500'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.2,
        staggerChildren: 0.1
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
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <motion.div 
            className="text-center"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.div 
              className="flex items-center justify-center mb-6"
              variants={itemVariants}
            >
              <div className="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/20">
                {user.type === 'veo_user' ? (
                  <Video className="w-10 h-10 text-white" />
                ) : (
                  <Zap className="w-10 h-10 text-white" />
                )}
              </div>
            </motion.div>

            <motion.h1 
              className="text-5xl md:text-6xl font-bold mb-6"
              variants={itemVariants}
            >
              Benvenuto, {user.name.split(' ')[0]}!
            </motion.h1>

            <motion.p 
              className="text-xl md:text-2xl mb-8 text-primary-100 max-w-3xl mx-auto"
              variants={itemVariants}
            >
              {user.type === 'veo_user' 
                ? 'Trasforma i tuoi testi in video straordinari con la potenza di Veo2/3'
                : 'Crea contenuti multimediali professionali con il nostro editor avanzato'
              }
            </motion.p>

            <motion.div 
              className="flex flex-col sm:flex-row gap-4 justify-center"
              variants={itemVariants}
            >
              <button
                onClick={() => setShowUpload(true)}
                className="bg-white text-primary-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-primary-50 transition-colors flex items-center space-x-2 shadow-lg"
              >
                <Upload className="w-5 h-5" />
                <span>Carica Testo</span>
              </button>
              
              <button
                onClick={() => navigate('/catalog')}
                className="bg-primary-500 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-primary-400 transition-colors flex items-center space-x-2 border border-primary-400"
              >
                <BookOpen className="w-5 h-5" />
                <span>Esplora Catalogo</span>
              </button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Come Funziona
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Il nostro processo AI trasforma automaticamente i tuoi testi in contenuti multimediali professionali
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="text-center group"
                >
                  <div className={`w-16 h-16 ${feature.color} rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-lg`}>
                    <IconComponent className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Il Tuo Workflow Personalizzato
            </h2>
            <div className="flex items-center justify-center space-x-2 mb-6">
              {user.type === 'veo_user' ? (
                <Video className="w-6 h-6 text-primary-600" />
              ) : (
                <Zap className="w-6 h-6 text-primary-600" />
              )}
              <span className="text-lg font-medium text-primary-600">
                {user.type === 'veo_user' ? 'Veo User Workflow' : 'Image Editor Workflow'}
              </span>
            </div>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {user.type === 'veo_user' ? (
              <>
                <motion.div 
                  className="card text-center"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6 }}
                >
                  <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">1. Analisi Testo</h3>
                  <p className="text-gray-600">Veo analizza il contenuto e identifica scene chiave per la generazione video</p>
                </motion.div>

                <motion.div 
                  className="card text-center"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <Video className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">2. Generazione Veo</h3>
                  <p className="text-gray-600">Veo2/3 genera direttamente video di alta qualità dalle descrizioni</p>
                </motion.div>

                <motion.div 
                  className="card text-center"
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  <div className="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">3. Validazione</h3>
                  <p className="text-gray-600">Controlli automatici assicurano coerenza e qualità del risultato finale</p>
                </motion.div>
              </>
            ) : (
              <>
                <motion.div 
                  className="card text-center"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6 }}
                >
                  <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <Image className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">1. Generazione Immagini</h3>
                  <p className="text-gray-600">Crea sequenze di immagini correlate e cronologicamente ordinate</p>
                </motion.div>

                <motion.div 
                  className="card text-center"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <Music className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">2. Audio & Editing</h3>
                  <p className="text-gray-600">Genera audio e usa l'editor video per combinare tutti gli elementi</p>
                </motion.div>

                <motion.div 
                  className="card text-center"
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <Clock className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">3. Finalizzazione</h3>
                  <p className="text-gray-600">Validazione finale e export del video MP4 professionale</p>
                </motion.div>
              </>
            )}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">
              Pronto a Iniziare?
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Trasforma le tue idee in contenuti multimediali straordinari con l'AI
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="bg-white text-primary-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-primary-50 transition-colors flex items-center justify-center space-x-2"
              >
                <span>Vai alla Dashboard</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* File Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <FileUpload 
              user={user} 
              onClose={() => setShowUpload(false)}
              onSuccess={(project) => {
                setShowUpload(false);
                navigate(`/project/${project.id}`);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
