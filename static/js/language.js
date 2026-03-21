// Language Translation System
const translations = {
  'en': {
    // Navigation
    'about': 'About',
    'projects': 'Projects',
    'services': 'Services',
    'tech': 'Tech Stack',
    'contact': 'Contact',
    
    // Hero Section
    'hero-title': "Hi, I'm Ziad Yakoot",
    'hero-subtitle': 'AI Engineer & Embedded Systems Developer',
    'hire-btn': 'Hire Me',
    'projects-btn': 'View Projects',
    
    // About Section
    'about-tag': 'Who I Am',
    'about-title': 'About Me',
    'about-desc': 'Passionate engineer building AI-driven products that solve real problems in healthcare and smart devices.',
    'about-heading': 'Building the Future, One AI at a Time',
    'medical-ai': 'AI Medical Devices',
    'smart-glasses': 'Smart Glasses',
    'ai-agents': 'AI Agents & Automation',
    'full-stack': 'Full-Stack Development',
    
    // Stats
    'years-exp': 'Years Experience',
    'projects-done': 'Projects Completed',
    'ai-models': 'AI Models Deployed',
    'dedication': 'Dedication',
    
    // Projects Section
    'projects-tag': 'My Work',
    'projects-title': 'Featured Projects',
    'projects-desc': "Real-world AI and embedded systems solutions I've built from the ground up.",
    'more-projects': 'More projects coming soon',
    
    // Services Section
    'services-tag': 'What I Offer',
    'services-title': 'Services',
    'services-desc': 'From AI model development to full hardware integration — I deliver end-to-end solutions.',
    'ai-ml': 'AI & Machine Learning',
    'embedded': 'Embedded Systems',
    'healthcare-tech': 'Healthcare Technology',
    'software-dev': 'Software Development',
    
    // Tech Stack Section
    'tech-tag': 'Skills',
    'tech-title': 'Tech Stack',
    'tech-desc': 'The tools and technologies I use to build AI-powered solutions.',
    'languages': 'Languages',
    'ai-data': 'AI & Data',
    'embedded-hw': 'Embedded & Hardware',
    'web-backend': 'Web & Backend',
    
    // GitHub Stats Section
    'github-tag': 'Open Source',
    'github-title': 'GitHub Stats',
    
    // Contact Section
    'contact-tag': 'Get In Touch',
    'contact-title': 'Contact Me',
    'contact-desc': "Have a project in mind? Let's build something amazing together.",
    'work-together': "Let's Work Together",
  },
  'ar': {
    // Navigation
    'about': 'عني',
    'projects': 'المشاريع',
    'services': 'الخدمات',
    'tech': 'المهارات',
    'contact': 'التواصل',
    
    // Hero Section
    'hero-title': 'مرحبا، أنا زياد ياقوت',
    'hero-subtitle': 'مهندس ذكاء اصطناعي ومطور الأنظمة المدمجة',
    'hire-btn': 'وظفني',
    'projects-btn': 'عرض المشاريع',
    
    // About Section
    'about-tag': 'من أنا',
    'about-title': 'عني',
    'about-desc': 'مهندس شغوف ببناء منتجات مدفوعة بالذكاء الاصطناعي تحل مشاكل حقيقية في الرعاية الصحية والأجهزة الذكية.',
    'about-heading': 'بناء المستقبل، ذكاء اصطناعي تلو الآخر',
    'medical-ai': 'أجهزة ذكية طبية',
    'smart-glasses': 'نظارات ذكية',
    'ai-agents': 'وكلاء ذكيين وأتمتة',
    'full-stack': 'تطوير التطبيقات الشاملة',
    
    // Stats
    'years-exp': 'سنوات من الخبرة',
    'projects-done': 'مشاريع مكتملة',
    'ai-models': 'نماذج ذكاء اصطناعي مُطلقة',
    'dedication': 'التفاني',
    
    // Projects Section
    'projects-tag': 'أعمالي',
    'projects-title': 'المشاريع المميزة',
    'projects-desc': 'حلول واقعية في مجال الذكاء الاصطناعي والأنظمة المدمجة التي بنيتها من الصفر.',
    'more-projects': 'مشاريع إضافية قريباً',
    
    // Services Section
    'services-tag': 'ما أقدمه',
    'services-title': 'الخدمات',
    'services-desc': 'من تطوير نماذج الذكاء الاصطناعي إلى التكامل الكامل للأجهزة - أقدم حلولاً شاملة.',
    'ai-ml': 'الذكاء الاصطناعي والتعلم الآلي',
    'embedded': 'الأنظمة المدمجة',
    'healthcare-tech': 'تقنيات الرعاية الصحية',
    'software-dev': 'تطوير البرامج',
    
    // Tech Stack Section
    'tech-tag': 'المهارات',
    'tech-title': 'مكدس التقنيات',
    'tech-desc': 'الأدوات والتقنيات التي أستخدمها لبناء حلول مدفوعة بالذكاء الاصطناعي.',
    'languages': 'لغات البرمجة',
    'ai-data': 'الذكاء الاصطناعي والبيانات',
    'embedded-hw': 'الأنظمة المدمجة والأجهزة',
    'web-backend': 'الويب والخادم الخلفي',
    
    // GitHub Stats Section
    'github-tag': 'المصدر المفتوح',
    'github-title': 'إحصائيات GitHub',
    
    // Contact Section
    'contact-tag': 'تواصل معي',
    'contact-title': 'اتصل بي',
    'contact-desc': 'هل لديك مشروع في الذاكرة؟ دعونا نبني شيئاً رائعاً معاً.',
    'work-together': 'دعنا نعمل معاً',
  }
};

function setLanguage(lang) {
  // Set HTML lang attribute
  document.getElementById('html-root').setAttribute('lang', lang);
  document.getElementById('body-root').setAttribute('lang', lang);
  
  // Save language preference
  localStorage.setItem('preferred-language', lang);
  
  // Update all elements with data attributes
  document.querySelectorAll('[data-en][data-ar]').forEach(element => {
    if (lang === 'ar') {
      element.textContent = element.getAttribute('data-ar');
    } else {
      element.textContent = element.getAttribute('data-en');
    }
  });
  
  // Update language toggle button
  const toggleBtn = document.getElementById('language-toggle');
  if (lang === 'ar') {
    toggleBtn.textContent = 'English';
  } else {
    toggleBtn.textContent = 'العربية';
  }
  
  // Update direction hint for nav links
  if (lang === 'ar') {
    document.body.classList.add('rtl');
  } else {
    document.body.classList.remove('rtl');
  }
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
  const savedLanguage = localStorage.getItem('preferred-language') || 'en';
  setLanguage(savedLanguage);
  
  // Language toggle button click handler
  const toggleBtn = document.getElementById('language-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentLang = document.getElementById('html-root').getAttribute('lang');
      const newLang = currentLang === 'en' ? 'ar' : 'en';
      setLanguage(newLang);
    });
  }
});
