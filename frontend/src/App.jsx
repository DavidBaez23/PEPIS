import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import logo from './assets/logo.png';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      role: 'assistant', 
      content: '¡Hola! Soy PEPIS, el Asistente Virtual Oficial del programa de Ingeniería de Sistemas de la UFPS. ¿En qué te puedo ayudar hoy?' 
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text) => {
    // Agregar mensaje del usuario
    const newUserMessage = { id: Date.now(), role: 'user', content: text };
    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // Formatear historial para el backend (excluyendo el mensaje actual y el saludo inicial)
      // Ajusta esto dependiendo de cómo el backend espera el historial
      const history = messages
        .filter(m => m.id !== 1) // Opcional: excluir saludo
        .map(m => ({
          role: m.role,
          content: m.content
        }));

      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          query: text,
          history: history
        })
      });

      if (!response.ok) {
        throw new Error('Error en la respuesta del servidor');
      }

      const data = await response.json();
      
      const newBotMessage = { 
        id: Date.now() + 1, 
        role: 'assistant', 
        content: data.answer 
      };
      
      setMessages((prev) => [...prev, newBotMessage]);
    } catch (error) {
      console.error("Error fetching chat:", error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Lo siento, ha ocurrido un error al conectar con el servidor. Por favor verifica que el backend esté ejecutándose.'
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo-container">
          <img src={logo} alt="PEPIS Logo" onError={(e) => { e.target.style.display = 'none'; }} />
        </div>
        <div className="header-text">
          <h1>PEPIS</h1>
          <p>Asistente Virtual - Ingeniería de Sistemas UFPS</p>
        </div>
      </header>
      
      <main className="chat-container">
        {messages.map((msg) => (
          <ChatMessage 
            key={msg.id} 
            message={msg.content} 
            isBot={msg.role === 'assistant'} 
          />
        ))}
        {isLoading && <ChatMessage isBot={true} isLoading={true} />}
        <div ref={messagesEndRef} />
      </main>

      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}

export default App;
