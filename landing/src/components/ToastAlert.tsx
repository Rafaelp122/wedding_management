import { useState, useEffect } from 'react';
import { Check, X } from 'lucide-react';

export default function ToastAlert() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleAlert = (event: Event) => {
      const customEvent = event as CustomEvent<string>;
      setMessage(customEvent.detail || 'Conta configurada. Verifique seu e-mail para validar o seu acesso.');
      setIsOpen(true);
    };

    window.addEventListener('custom-alert', handleAlert);

    return () => {
      window.removeEventListener('custom-alert', handleAlert);
    };
  }, []);

  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        setIsOpen(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const hideAlert = () => setIsOpen(false);

  return (
    <div
      className={`fixed bottom-6 right-6 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 shadow-2xl rounded-lg p-4 flex items-start gap-3 transition-all duration-300 z-50 max-w-sm ${
        isOpen ? 'translate-y-0 opacity-100' : 'translate-y-20 opacity-0 pointer-events-none'
      }`}
    >
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-600 mt-0.5">
        <Check className="w-4 h-4" />
      </div>
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-zinc-900 dark:text-white font-display">Sim, Aceito! ERP Ativado</h4>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">{message}</p>
      </div>
      <button
        onClick={hideAlert}
        aria-label="Fechar notificação"
        className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
