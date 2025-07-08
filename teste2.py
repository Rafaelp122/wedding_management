<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HarmonyWed - Gestão de Casamentos para Cerimonialistas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
        }
        .btn-primary {
            background-color: #9C27B0;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            background-color: #7B1FA2;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        .testimonial-card {
            background-color: #fff9e6;
        }
        .pricing-card:hover {
            transform: scale(1.03);
        }
        .pricing-popular {
            border: 2px solid #9C27B0;
        }
    </style>
</head>
<body class="font-sans bg-white text-gray-800">
    <!-- Header/Navbar -->
    <nav class="bg-white sticky top-0 z-50 shadow-sm">
        <div class="container mx-auto px-4 py-3 flex justify-between items-center">
            <div class="flex items-center">
                <img src="https://via.placeholder.com/50x50" alt="HarmonyWed Logo" class="h-10 mr-2">
                <span class="text-xl font-bold text-purple-800">HarmonyWed</span>
            </div>
            
            <div class="hidden md:flex items-center space-x-8">
                <a href="#about" class="text-gray-700 hover:text-purple-800 transition">Sobre</a>
                <a href="#benefits" class="text-gray-700 hover:text-purple-800 transition">Benefícios</a>
                <a href="#features" class="text-gray-700 hover:text-purple-800 transition">Recursos</a>
                <a href="#pricing" class="text-gray-700 hover:text-purple-800 transition">Planos</a>
                <a href="#contact" class="text-gray-700 hover:text-purple-800 transition">Fale Conosco</a>
            </div>
            
            <button class="md:hidden text-gray-700 focus:outline-none">
                <i class="fas fa-bars text-2xl"></i>
            </button>
            
            <button class="hidden md:block bg-purple-800 text-white px-6 py-2 rounded-full hover:bg-purple-700 transition">
                Login / Cadastro
            </button>
        </div>
        
        <!-- Mobile menu -->
        <div class="md:hidden hidden bg-white py-4 px-4 shadow-md">
            <a href="#about" class="block py-2 text-gray-700 hover:text-purple-800">Sobre</a>
            <a href="#benefits" class="block py-2 text-gray-700 hover:text-purple-800">Benefícios</a>
            <a href="#features" class="block py-2 text-gray-700 hover:text-purple-800">Recursos</a>
            <a href="#pricing" class="block py-2 text-gray-700 hover:text-purple-800">Planos</a>
            <a href="#contact" class="block py-2 text-gray-700 hover:text-purple-800">Fale Conosco</a>
            <button class="w-full mt-2 bg-purple-800 text-white px-6 py-2 rounded-full hover:bg-purple-700 transition">
                Login / Cadastro
            </button>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="gradient-bg text-white py-20">
        <div class="container mx-auto px-4 flex flex-col md:flex-row items-center">
            <div class="md:w-1/2 mb-10 md:mb-0">
                <h1 class="text-4xl md:text-5xl font-bold mb-6">Transforme sua Gestão de Casamentos</h1>
                <p class="text-xl mb-8">O sistema completo para cerimonialistas que desejam organizar, planejar e executar casamentos perfeitos com menos estresse e mais eficiência.</p>
                <div class="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                    <button class="bg-white text-purple-800 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition">
                        Experimente Grátis
                    </button>
                    <button class="border-2 border-white text-white px-8 py-3 rounded-full font-semibold hover:bg-white hover:text-purple-800 transition">
                        Ver Demonstração
                    </button>
                </div>
            </div>
            <div class="md:w-1/2">
                <img src="https://via.placeholder.com/600x400" alt="Dashboard HarmonyWed" class="rounded-lg shadow-2xl">
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-20 bg-white">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold text-purple-800 mb-4">Sobre o HarmonyWed</h2>
                <p class="text-xl text-gray-600 max-w-3xl mx-auto">A solução completa para cerimonialistas profissionais que buscam excelência na organização de casamentos.</p>
            </div>
            
            <div class="flex flex-col md:flex-row items-center">
                <div class="md:w-1/2 mb-10 md:mb-0">
                    <img src="https://via.placeholder.com/500x350" alt="Cerimonialista trabalhando" class="rounded-lg shadow-lg">
                </div>
                <div class="md:w-1/2 md:pl-12">
                    <h3 class="text-2xl font-bold text-gray-800 mb-6">Sua carreira de cerimonialista merece o melhor</h3>
                    <p class="text-gray-600 mb-6">O HarmonyWed foi desenvolvido por especialistas em cerimoniais para atender às necessidades específicas dos profissionais que desejam oferecer um serviço impecável aos noivos.</p>
                    <p class="text-gray-600 mb-6">Com anos de experiência no mercado, entendemos os desafios da profissão e criamos ferramentas que realmente fazem a diferença no seu dia a dia.</p>
                    <div class="flex items-center">
                        <i class="fas fa-check-circle text-purple-800 text-2xl mr-3"></i>
                        <span class="text-gray-700">Mais de 500 cerimonialistas já confiam em nossa plataforma</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Benefits Section -->
    <section id="benefits" class="py-20 bg-gray-50">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold text-purple-800 mb-4">Benefícios Exclusivos</h2>
                <p class="text-xl text-gray-600 max-w-3xl mx-auto">Tudo o que você precisa para elevar seu serviço de cerimonial a outro nível</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div class="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition feature-card">
                    <div class="text-purple-800 text-4xl mb-4">
                        <i class="fas fa-clock"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Economize Tempo</h3>
                    <p class="text-gray-600">Automatize processos repetitivos e dedique mais tempo ao que realmente importa: seus clientes.</p>
                </div>
                
                <div class="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition feature-card">
                    <div class="text-purple-800 text-4xl mb-4">
                        <i class="fas fa-bell"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Lembretes Inteligentes</h3>
                    <p class="text-gray-600">Nunca mais perca prazos importantes com nosso sistema de alertas personalizados.</p>
                </div>
                
                <div class="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition feature-card">
                    <div class="text-purple-800 text-4xl mb-4">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Relatórios Profissionais</h3>
                    <p class="text-gray-600">Gere relatórios detalhados para mostrar o valor do seu trabalho aos noivos.</p>
                </div>
                
                <div class="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition feature-card">
                    <div class="text-purple-800 text-4xl mb-4">
                        <i class="fas fa-users"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Gestão de Convidados</h3>
                    <p class="text-gray-600">Controle completo da lista de convidados, confirmações e restrições alimentares.</p>
                </div>
                
                <div class="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition feature-card">
                    <div class="text-purple-800 text-4xl mb-4">
                        <i class="fas fa-calendar-check"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Agenda Integrada</h3>
                    <p class="text-gray-600">Visualize todos seus compromissos e eventos em um calendário intuitivo.</p>
                </div>
                
                <div class="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition feature-card">
                    <div class="text-purple-800 text-4xl mb-4">
                        <i class="fas fa-file-contract"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Contratos Automatizados</h3>
                    <p class="text-gray-600">Gere contratos profissionais em minutos com nossos modelos personalizáveis.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 bg-white">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold text-purple-800 mb-4">Recursos Poderosos</h2>
                <p class="text-xl text-gray-600 max-w-3xl mx-auto">Ferramentas desenvolvidas especialmente para cerimonialistas</p>
            </div>
            
            <div class="flex flex-col md:flex-row items-center mb-16">
                <div class="md:w-1/2 mb-10 md:mb-0 md:pr-10">
                    <h3 class="text-2xl font-bold text-gray-800 mb-6">Checklists Personalizáveis</h3>
                    <p class="text-gray-600 mb-6">Crie checklists completos para cada etapa do casamento, desde o noivado até o dia da cerimônia.</p>
                    <ul class="space-y-3">
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Modelos prontos para diferentes tipos de casamento</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Compartilhamento com os noivos</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Marcador de tarefas concluídas</span>
                        </li>
                    </ul>
                </div>
                <div class="md:w-1/2">
                    <img src="https://via.placeholder.com/500x350" alt="Checklists" class="rounded-lg shadow-lg">
                </div>
            </div>
            
            <div class="flex flex-col md:flex-row items-center mb-16">
                <div class="md:w-1/2 order-1 md:order-2 mb-10 md:mb-0 md:pl-10">
                    <h3 class="text-2xl font-bold text-gray-800 mb-6">Orçamento Detalhado</h3>
                    <p class="text-gray-600 mb-6">Controle todos os custos do casamento em uma ferramenta intuitiva que ajuda a evitar surpresas.</p>
                    <ul class="space-y-3">
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Categorização automática de despesas</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Alertas quando o orçamento está próximo do limite</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Relatórios gráficos para apresentação aos noivos</span>
                        </li>
                    </ul>
                </div>
                <div class="md:w-1/2 order-2 md:order-1">
                    <img src="https://via.placeholder.com/500x350" alt="Orçamento" class="rounded-lg shadow-lg">
                </div>
            </div>
            
            <div class="flex flex-col md:flex-row items-center">
                <div class="md:w-1/2 mb-10 md:mb-0 md:pr-10">
                    <h3 class="text-2xl font-bold text-gray-800 mb-6">Cronograma do Dia</h3>
                    <p class="text-gray-600 mb-6">Planeje minuto a minuto do grande dia com uma ferramenta visual que facilita a coordenação.</p>
                    <ul class="space-y-3">
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Linha do tempo interativa</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Compartilhamento com fornecedores</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Versão impressa para o dia do evento</span>
                        </li>
                    </ul>
                </div>
                <div class="md:w-1/2">
                    <img src="https://via.placeholder.com/500x350" alt="Cronograma" class="rounded-lg shadow-lg">
                </div>
            </div>
        </div>
    </section>

    <!-- Testimonials Section -->
    <section class="py-20 bg-purple-800 text-white">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold mb-4">O que dizem nossos clientes</h2>
                <p class="text-xl max-w-3xl mx-auto">Cerimonialistas que transformaram seus negócios com o HarmonyWed</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="testimonial-card p-8 rounded-lg text-gray-800">
                    <div class="flex items-center mb-4">
                        <img src="https://via.placeholder.com/50x50" alt="Cliente" class="rounded-full h-12 w-12 mr-4">
                        <div>
                            <h4 class="font-bold">Ana Carolina</h4>
                            <p class="text-sm text-gray-600">Cerimonialista há 8 anos</p>
                        </div>
                    </div>
                    <p class="mb-4">"O HarmonyWed revolucionou minha forma de trabalhar. Agora consigo atender mais casais sem perder a qualidade do meu serviço."</p>
                    <div class="text-yellow-400">
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                    </div>
                </div>
                
                <div class="testimonial-card p-8 rounded-lg text-gray-800">
                    <div class="flex items-center mb-4">
                        <img src="https://via.placeholder.com/50x50" alt="Cliente" class="rounded-full h-12 w-12 mr-4">
                        <div>
                            <h4 class="font-bold">Ricardo Almeida</h4>
                            <p class="text-sm text-gray-600">Cerimonialista há 5 anos</p>
                        </div>
                    </div>
                    <p class="mb-4">"Os noivos ficam impressionados com a organização e profissionalismo que o sistema me permite demonstrar. Virou meu diferencial no mercado."</p>
                    <div class="text-yellow-400">
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                    </div>
                </div>
                
                <div class="testimonial-card p-8 rounded-lg text-gray-800">
                    <div class="flex items-center mb-4">
                        <img src="https://via.placeholder.com/50x50" alt="Cliente" class="rounded-full h-12 w-12 mr-4">
                        <div>
                            <h4 class="font-bold">Fernanda Gomes</h4>
                            <p class="text-sm text-gray-600">Cerimonialista há 12 anos</p>
                        </div>
                    </div>
                    <p class="mb-4">"Depois de anos usando planilhas e cadernos, descobri o HarmonyWed e não consigo mais trabalhar sem. Vale cada centavo investido!"</p>
                    <div class="text-yellow-400">
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star-half-alt"></i>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section id="pricing" class="py-20 bg-white">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold text-purple-800 mb-4">Planos que se adaptam a você</h2>
                <p class="text-xl text-gray-600 max-w-3xl mx-auto">Escolha o plano ideal para o tamanho do seu negócio</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                <div class="bg-white border border-gray-200 rounded-lg p-8 shadow-md hover:shadow-xl transition pricing-card">
                    <h3 class="text-xl font-bold text-center mb-4">Básico</h3>
                    <div class="text-center mb-6">
                        <span class="text-4xl font-bold text-purple-800">R$ 49</span>
                        <span class="text-gray-600">/mês</span>
                    </div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Até 3 casamentos simultâneos</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Checklists básicos</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Gestão de convidados</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Suporte por e-mail</span>
                        </li>
                    </ul>
                    <button class="w-full bg-gray-200 text-gray-800 py-3 rounded-full font-semibold hover:bg-gray-300 transition">
                        Começar
                    </button>
                </div>
                
                <div class="bg-white border-2 border-purple-800 rounded-lg p-8 shadow-xl relative pricing-card pricing-popular">
                    <div class="absolute top-0 right-0 bg-purple-800 text-white px-4 py-1 rounded-bl-lg rounded-tr-lg text-sm font-semibold">
                        Mais Popular
                    </div>
                    <h3 class="text-xl font-bold text-center mb-4">Profissional</h3>
                    <div class="text-center mb-6">
                        <span class="text-4xl font-bold text-purple-800">R$ 89</span>
                        <span class="text-gray-600">/mês</span>
                    </div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Até 10 casamentos simultâneos</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Checklists completos e personalizáveis</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Gestão avançada de convidados</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Orçamento detalhado</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Suporte prioritário</span>
                        </li>
                    </ul>
                    <button class="w-full bg-purple-800 text-white py-3 rounded-full font-semibold hover:bg-purple-700 transition">
                        Começar
                    </button>
                </div>
                
                <div class="bg-white border border-gray-200 rounded-lg p-8 shadow-md hover:shadow-xl transition pricing-card">
                    <h3 class="text-xl font-bold text-center mb-4">Premium</h3>
                    <div class="text-center mb-6">
                        <span class="text-4xl font-bold text-purple-800">R$ 149</span>
                        <span class="text-gray-600">/mês</span>
                    </div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Casamentos ilimitados</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Todos os recursos profissionais</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Relatórios personalizados</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Contratos automatizados</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Suporte 24/7</span>
                        </li>
                        <li class="flex items-start">
                            <i class="fas fa-check text-purple-800 mt-1 mr-2"></i>
                            <span>Treinamento personalizado</span>
                        </li>
                    </ul>
                    <button class="w-full bg-gray-200 text-gray-800 py-3 rounded-full font-semibold hover:bg-gray-300 transition">
                        Começar
                    </button>
                </div>
            </div>
            
            <div class="text-center mt-12">
                <p class="text-gray-600 mb-4">Precisa de um plano personalizado para sua equipe?</p>
                <button class="border-2 border-purple-800 text-purple-800 px-8 py-3 rounded-full font-semibold hover:bg-purple-800 hover:text-white transition">
                    Fale com nosso time
                </button>
            </div>
        </div>
    </section>

    <!-- FAQ Section -->
    <section class="py-20 bg-gray-50">
        <div class="container mx-auto px-4 max-w-4xl">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold text-purple-800 mb-4">Perguntas Frequentes</h2>
                <p class="text-xl text-gray-600">Tire suas dúvidas sobre o HarmonyWed</p>
            </div>
            
            <div class="space-y-6">
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-xl font-bold mb-3 flex justify-between items-center cursor-pointer">
                        <span>O HarmonyWed é difícil de usar?</span>
                        <i class="fas fa-chevron-down text-purple-800"></i>
                    </h3>
                    <div class="hidden text-gray-600 mt-2">
                        <p>Não! Desenvolvemos a plataforma pensando na facilidade de uso. Mesmo cerimonialistas que não têm muita familiaridade com tecnologia conseguem usar todas as funcionalidades com pouco tempo de adaptação. Além disso, oferecemos tutoriais em vídeo e suporte sempre que precisar.</p>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-xl font-bold mb-3 flex justify-between items-center cursor-pointer">
                        <span>Posso testar antes de assinar?</span>
                        <i class="fas fa-chevron-down text-purple-800"></i>
                    </h3>
                    <div class="hidden text-gray-600 mt-2">
                        <p>Sim! Oferecemos um período de teste gratuito de 14 dias para você explorar todas as funcionalidades da plataforma sem compromisso. Não pedimos cartão de crédito para o teste, você só precisará criar uma conta.</p>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-xl font-bold mb-3 flex justify-between items-center cursor-pointer">
                        <span>Meus dados estarão seguros?</span>
                        <i class="fas fa-chevron-down text-purple-800"></i>
                    </h3>
                    <div class="hidden text-gray-600 mt-2">
                        <p>Absolutamente. Utilizamos criptografia de ponta a ponta para proteger todas as informações dos seus clientes e dos casamentos que você gerencia. Fazemos backups diários e seguimos rigorosos protocolos de segurança para garantir a integridade dos seus dados.</p>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-xl font-bold mb-3 flex justify-between items-center cursor-pointer">
                        <span>Posso cancelar quando quiser?</span>
                        <i class="fas fa-chevron-down text-purple-800"></i>
                    </h3>
                    <div class="hidden text-gray-600 mt-2">
                        <p>Sim, não há fidelidade. Você pode cancelar seu plano a qualquer momento diretamente na plataforma. Se cancelar no meio do período, terá acesso até o final do mês já pago.</p>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-xl font-bold mb-3 flex justify-between items-center cursor-pointer">
                        <span>O sistema funciona no celular?</span>
                        <i class="fas fa-chevron-down text-purple-800"></i>
                    </h3>
                    <div class="hidden text-gray-600 mt-2">
                        <p>Sim! O HarmonyWed é totalmente responsivo e funciona perfeitamente em smartphones e tablets. Também oferecemos um aplicativo nativo para iOS e Android com funcionalidades essenciais para quando você estiver no local do evento.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-20 bg-white">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold text-purple-800 mb-4">Fale Conosco</h2>
                <p class="text-xl text-gray-600 max-w-3xl mx-auto">Tem dúvidas ou sugestões? Estamos aqui para ajudar!</p>
            </div>
            
            <div class="flex flex-col md:flex-row">
                <div class="md:w-1/2 mb-10 md:mb-0 md:pr-10">
                    <form class="space-y-6">
                        <div>
                            <label for="name" class="block text-gray-700 font-medium mb-2">Seu Nome</label>
                            <input type="text" id="name" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-800">
                        </div>
                        
                        <div>
                            <label for="email" class="block text-gray-700 font-medium mb-2">Seu E-mail</label>
                            <input type="email" id="email" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-800">
                        </div>
                        
                        <div>
                            <label for="subject" class="block text-gray-700 font-medium mb-2">Assunto</label>
                            <select id="subject" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-800">
                                <option value="">Selecione um assunto</option>
                                <option value="support">Suporte Técnico</option>
                                <option value="sales">Dúvidas sobre Planos</option>
                                <option value="partnership">Parcerias</option>
                                <option value="other">Outro</option>
                            </select>
                        </div>
                        
                        <div>
                            <label for="message" class="block text-gray-700 font-medium mb-2">Sua Mensagem</label>
                            <textarea id="message" rows="5" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-800"></textarea>
                        </div>
                        
                        <button type="submit" class="w-full bg-purple-800 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition">
                            Enviar Mensagem
                        </button>
                    </form>
                </div>
                
                <div class="md:w-1/2 md:pl-10">
                    <div class="bg-gray-50 p-8 rounded-lg h-full">
                        <h3 class="text-xl font-bold text-gray-800 mb-6">Outras formas de contato</h3>
                        
                        <div class="space-y-6">
                            <div class="flex items-start">
                                <div class="text-purple-800 text-2xl mr-4">
                                    <i class="fas fa-envelope"></i>
                                </div>
                                <div>
                                    <h4 class="font-bold text-gray-800">E-mail</h4>
                                    <p class="text-gray-600">contato@harmonywed.com.br</p>
                                </div>
                            </div>
                            
                            <div class="flex items-start">
                                <div class="text-purple-800 text-2xl mr-4">
                                    <i class="fas fa-phone-alt"></i>
                                </div>
                                <div>
                                    <h4 class="font-bold text-gray-800">Telefone</h4>
                                    <p class="text-gray-600">(11) 1234-5678</p>
                                    <p class="text-sm text-gray-500">Segunda a sexta, das 9h às 18h</p>
                                </div>
                            </div>
                            
                            <div class="flex items-start">
                                <div class="text-purple-800 text-2xl mr-4">
                                    <i class="fas fa-map-marker-alt"></i>
                                </div>
                                <div>
                                    <h4 class="font-bold text-gray-800">Endereço</h4>
                                    <p class="text-gray-600">Av. Paulista, 1000 - São Paulo/SP</p>
                                </div>
                            </div>
                            
                            <div class="flex items-start">
                                <div class="text-purple-800 text-2xl mr-4">
                                    <i class="fas fa-comment-dots"></i>
                                </div>
                                <div>
                                    <h4 class="font-bold text-gray-800">Redes Sociais</h4>
                                    <div class="flex space-x-4 mt-2">
                                        <a href="#" class="text-purple-800 hover:text-purple-600 text-2xl">
                                            <i class="fab fa-facebook"></i>
                                        </a>
                                        <a href="#" class="text-purple-800 hover:text-purple-600 text-2xl">
                                            <i class="fab fa-instagram"></i>
                                        </a>
                                        <a href="#" class="text-purple-800 hover:text-purple-600 text-2xl">
                                            <i class="fab fa-linkedin"></i>
                                        </a>
                                        <a href="#" class="text-purple-800 hover:text-purple-600 text-2xl">
                                            <i class="fab fa-whatsapp"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 gradient-bg text-white">
        <div class="container mx-auto px-4 text-center">
            <h2 class="text-3xl font-bold mb-6">Pronto para transformar sua carreira de cerimonialista?</h2>
            <p class="text-xl mb-8 max-w-3xl mx-auto">Junte-se a centenas de profissionais que já usam o HarmonyWed para oferecer um serviço excepcional aos noivos.</p>
            <button class="bg-white text-purple-800 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition">
                Comece Agora - 14 Dias Grátis
            </button>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
        <div class="container mx-auto px-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                    <div class="flex items-center mb-4">
                        <img src="https://via.placeholder.com/40x40" alt="Logo" class="h-8 mr-2">
                        <span class="text-xl font-bold">HarmonyWed</span>
                    </div>
                    <p class="text-gray-400">A solução completa para cerimonialistas que buscam excelência na organização de casamentos.</p>
                </div>
                
                <div>
                    <h4 class="text-lg font-semibold mb-4">Links Rápidos</h4>
                    <ul class="space-y-2">
                        <li><a href="#about" class="text-gray-400 hover:text-white transition">Sobre</a></li>
                        <li><a href="#benefits" class="text-gray-400 hover:text-white transition">Benefícios</a></li>
                        <li><a href="#features" class="text-gray-400 hover:text-white transition">Recursos</a></li>
                        <li><a href="#pricing" class="text-gray-400 hover:text-white transition">Planos</a></li>
                        <li><a href="#contact" class="text-gray-400 hover:text-white transition">Contato</a></li>
                    </ul>
                </div>
                
                <div>
                    <h4 class="text-lg font-semibold mb-4">Legal</h4>
                    <ul class="space-y-2">
                        <li><a href="#" class="text-gray-400 hover:text-white transition">Termos de Uso</a></li>
                        <li><a href="#" class="text-gray-400 hover:text-white transition">Política de Privacidade</a></li>
                        <li><a href="#" class="text-gray-400 hover:text-white transition">Cookies</a></li>
                    </ul>
                </div>
                
                <div>
                    <h4 class="text-lg font-semibold mb-4">Assine nossa newsletter</h4>
                    <p class="text-gray-400 mb-4">Receba dicas e novidades para cerimonialistas.</p>
                    <div class="flex">
                        <input type="email" placeholder="Seu e-mail" class="px-4 py-2 rounded-l-lg focus:outline-none text-gray-800 w-full">
                        <button class="bg-purple-800 px-4 py-2 rounded-r-lg hover:bg-purple-700 transition">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
                <p class="text-gray-400 mb-4 md:mb-0">© 2023 HarmonyWed. Todos os direitos reservados.</p>
                <div class="flex space-x-6">
                    <a href="#" class="text-gray-400 hover:text-white transition">
                        <i class="fab fa-facebook-f"></i>
                    </a>
                    <a href="#" class="text-gray-400 hover:text-white transition">
                        <i class="fab fa-instagram"></i>
                    </a>
                    <a href="#" class="text-gray-400 hover:text-white transition">
                        <i class="fab fa-linkedin-in"></i>
                    </a>
                    <a href="#" class="text-gray-400 hover:text-white transition">
                        <i class="fab fa-youtube"></i>
                    </a>
                </div>
            </div>
        </div>
    </footer>

    <script>
        // Mobile menu toggle
        document.querySelector('.md\\:hidden').addEventListener('click', function() {
            const menu = document.querySelector('.md\\:hidden + .hidden');
            menu.classList.toggle('hidden');
        });

        // FAQ accordion
        const faqItems = document.querySelectorAll('#faq h3');
        faqItems.forEach(item => {
            item.addEventListener('click', function() {
                const answer = this.nextElementSibling;
                const icon = this.querySelector('i');
                
                if (answer.classList.contains('hidden')) {
                    answer.classList.remove('hidden');
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-up');
                } else {
                    answer.classList.add('hidden');
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                }
            });
        });

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                    
                    // Close mobile menu if open
                    const mobileMenu = document.querySelector('.md\\:hidden + .hidden');
                    if (!mobileMenu.classList.contains('hidden')) {
                        mobileMenu.classList.add('hidden');
                    }
                }
            });
        });
    </script>
</body>
</html>