import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Turkish translations
const tr = {
  app: {
    name: 'BorçTakip',
    welcome: 'Hoş geldiniz!',
    joinUs: 'Bize katılın!'
  },
  auth: {
    login: 'Giriş Yap',
    register: 'Kayıt Ol',
    logout: 'Çıkış Yap',
    email: 'E-posta Adresi',
    password: 'Şifre',
    fullName: 'Ad Soyad',
    emailPlaceholder: 'E-posta adresinizi girin',
    passwordPlaceholder: 'Şifrenizi girin',
    fullNamePlaceholder: 'Ad ve soyadınızı girin',
    processing: 'İşleniyor...',
    signIn: 'Giriş Yap',
    signUp: 'Kayıt Ol',
    noAccount: 'Hesabınız yok mu? Kayıt olun',
    hasAccount: 'Hesabınız var mı? Giriş yapın',
    loginError: 'Giriş yapılırken bir hata oluştu',
    registerError: 'Kayıt olurken bir hata oluştu',
    invalidCredentials: 'Geçersiz e-posta veya şifre',
    emailAlreadyExists: 'Bu e-posta adresi zaten kayıtlı'
  },
  dashboard: {
    title: 'Gösterge Paneli',
    loading: 'Gösterge paeli yükleniyor...',
    totalOwed: 'Toplam Borç',
    totalToCollect: 'Toplam Alacak',
    netBalance: 'Net Bakiye',
    activeDebts: 'Aktif Borçlar',
    quickAdd: 'Hızlı Ekle',
    keyInsights: 'Önemli Bilgiler',
    personOweMost: 'En çok borçlu olduğunuz kişi',
    mostOverdue: 'En çok geciken borç',
    noDebts: 'Henüz borç kaydınız yok',
    noDebtsDesc: 'İlk borç kaydınızı ekleyerek başlayın',
    days: 'gün',
    none: 'Yok'
  },
  debt: {
    yourDebts: 'Borçlarınız',
    youOwe: 'Borçlusunuz',
    theyOwe: 'Alacaklısınız',
    markPaid: 'Ödendi Olarak İşaretle',
    markUnpaid: 'Ödenmedi Olarak İşaretle',
    addDebt: 'Yeni Borç Ekle',
    editDebt: 'Borç Düzenle',
    deleteDebt: 'Borç Sil',
    debtType: 'Borç Türü',
    iOwe: 'Ben borçluyum',
    theyOweMe: 'O bana borçlu',
    personName: 'Kişi Adı',
    personNamePlaceholder: 'Kişinin adını girin',
    amount: 'Tutar',
    amountPlaceholder: '0,00',
    currency: 'Para Birimi',
    category: 'Kategori',
    description: 'Açıklama',
    descriptionPlaceholder: 'Bu borç hakkında açıklama yazın...',
    dueDate: 'Vade Tarihi',
    dueDateOptional: 'Vade Tarihi (İsteğe Bağlı)',
    noDueDate: 'Vade tarihi yok',
    cancel: 'İptal',
    save: 'Kaydet',
    adding: 'Ekleniyor...',
    saving: 'Kaydediliyor...',
    deleting: 'Siliniyor...',
    delete: 'Sil',
    edit: 'Düzenle',
    due: 'Vade',
    overdue: 'Gecikmiş',
    paid: 'Ödendi',
    unpaid: 'Ödenmedi',
    partiallyPaid: 'Kısmen Ödendi',
    active: 'Aktif',
    status: 'Durum'
  },
  category: {
    personalLoan: 'Kişisel Kredi',
    rent: 'Kira',
    sharedExpense: 'Ortak Gider',
    businessLoan: 'İş Kredisi',
    education: 'Eğitim',
    other: 'Diğer'
  },
  currency: {
    try: 'TRY',
    usd: 'USD',
    eur: 'EUR'
  },
  messages: {
    success: 'Başarılı',
    error: 'Hata',
    debtAdded: 'Borç başarıyla eklendi',
    debtUpdated: 'Borç başarıyla güncellendi',
    debtDeleted: 'Borç başarıyla silindi',
    debtMarkedPaid: 'Borç ödendi olarak işaretlendi',
    debtMarkedUnpaid: 'Borç ödenmedi olarak işaretlendi',
    networkError: 'Ağ hatası oluştu',
    unknownError: 'Bilinmeyen bir hata oluştu',
    fillAllFields: 'Lütfen tüm alanları doldurun',
    confirmDelete: 'Bu borcu silmek istediğinizden emin misiniz?',
    installApp: 'Uygulamayı Yükle',
    installAppDesc: 'Bu uygulamayı ana ekranınıza ekleyerek daha kolay erişim sağlayın',
    notificationsEnabled: 'Bildirimler etkinleştirildi',
    notificationsDisabled: 'Bildirimler devre dışı bırakıldı'
  },
  pwa: {
    installPrompt: 'Bu uygulamayı telefonunuza yükleyebilirsiniz',
    install: 'Yükle',
    later: 'Daha Sonra',
    offlineMode: 'Çevrimdışı Mod',
    onlineMode: 'Çevrimiçi Mod',
    updateAvailable: 'Güncelleme Mevcut',
    updateApp: 'Uygulamayı Güncelle'
  }
};

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  const login = (tokenData) => {
    setToken(tokenData.access_token);
    localStorage.setItem('token', tokenData.access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access_token}`;
    setUser({ authenticated: true });
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// PWA Hook
const usePWA = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstallable, setIsInstallable] = useState(false);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const installApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        setDeferredPrompt(null);
        setIsInstallable(false);
      }
    }
  };

  return { isInstallable, installApp };
};

// Notification Hook
const useNotifications = () => {
  const [permission, setPermission] = useState(Notification.permission);

  const requestPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      setPermission(permission);
      return permission === 'granted';
    }
    return false;
  };

  const showNotification = (title, options) => {
    if (permission === 'granted') {
      new Notification(title, {
        icon: '/icon-192.png',
        badge: '/icon-192.png',
        ...options
      });
    }
  };

  return { permission, requestPermission, showNotification };
};

// Components
const LoginForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLogin ? '/login' : '/register';
      const response = await axios.post(`${API}${endpoint}`, formData);
      login(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || tr.messages.unknownError;
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl font-bold">₺</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">{tr.app.name}</h1>
          <p className="text-gray-600 mt-2">
            {isLogin ? tr.app.welcome : tr.app.joinUs}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {tr.auth.fullName}
              </label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={tr.auth.fullNamePlaceholder}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {tr.auth.email}
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={tr.auth.emailPlaceholder}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {tr.auth.password}
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={tr.auth.passwordPlaceholder}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
          >
            {loading ? tr.auth.processing : (isLogin ? tr.auth.signIn : tr.auth.signUp)}
          </button>
        </form>

        <div className="mt-8 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-blue-500 hover:text-blue-600 font-medium"
          >
            {isLogin ? tr.auth.noAccount : tr.auth.hasAccount}
          </button>
        </div>
      </div>
    </div>
  );
};

const InstallPrompt = () => {
  const { isInstallable, installApp } = usePWA();
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    if (isInstallable) {
      const hasSeenPrompt = localStorage.getItem('pwa-install-prompt-seen');
      if (!hasSeenPrompt) {
        setShowPrompt(true);
      }
    }
  }, [isInstallable]);

  const handleInstall = () => {
    installApp();
    setShowPrompt(false);
    localStorage.setItem('pwa-install-prompt-seen', 'true');
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-prompt-seen', 'true');
  };

  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50">
      <div className="bg-white rounded-lg shadow-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="font-medium text-gray-900 mb-1">
              {tr.messages.installApp}
            </h3>
            <p className="text-sm text-gray-600">
              {tr.messages.installAppDesc}
            </p>
          </div>
          <div className="flex space-x-2 ml-4">
            <button
              onClick={handleDismiss}
              className="px-3 py-1 text-sm text-gray-500 hover:text-gray-700"
            >
              {tr.pwa.later}
            </button>
            <button
              onClick={handleInstall}
              className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
            >
              {tr.pwa.install}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [debts, setDebts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const { logout } = useAuth();
  const { showNotification, requestPermission } = useNotifications();

  useEffect(() => {
    fetchDashboardData();
    requestPermission();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, debtsResponse] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/debts`)
      ]);
      setStats(statsResponse.data);
      setDebts(debtsResponse.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsPaid = async (debtId) => {
    try {
      await axios.post(`${API}/debts/${debtId}/mark-paid`);
      showNotification(tr.messages.success, {
        body: tr.messages.debtMarkedPaid
      });
      fetchDashboardData();
    } catch (error) {
      console.error('Error marking debt as paid:', error);
    }
  };

  const markAsUnpaid = async (debtId) => {
    try {
      // Implement endpoint for marking as unpaid
      await axios.post(`${API}/debts/${debtId}/mark-unpaid`);
      showNotification(tr.messages.success, {
        body: tr.messages.debtMarkedUnpaid
      });
      fetchDashboardData();
    } catch (error) {
      console.error('Error marking debt as unpaid:', error);
    }
  };

  const formatCurrency = (amount, currency = 'TRY') => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return tr.debt.noDueDate;
    return new Date(dateString).toLocaleDateString('tr-TR');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-yellow-100 text-yellow-800';
      case 'paid': return 'bg-green-100 text-green-800';
      case 'partially_paid': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return tr.debt.active;
      case 'paid': return tr.debt.paid;
      case 'partially_paid': return tr.debt.partiallyPaid;
      default: return status;
    }
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'personal_loan': tr.category.personalLoan,
      'rent': tr.category.rent,
      'shared_expense': tr.category.sharedExpense,
      'business_loan': tr.category.businessLoan,
      'education': tr.category.education,
      'other': tr.category.other
    };
    return labels[category] || category;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">{tr.dashboard.loading}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center mr-3">
                <span className="text-white text-xl font-bold">₺</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">{tr.app.name}</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowAddForm(true)}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
              >
                {tr.dashboard.quickAdd}
              </button>
              <button
                onClick={logout}
                className="text-gray-500 hover:text-gray-700"
              >
                {tr.auth.logout}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                  <span className="text-red-600 text-lg">📉</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{tr.dashboard.totalOwed}</p>
                <p className="text-2xl font-bold text-red-600">
                  {formatCurrency(stats?.total_owed || 0)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 text-lg">📈</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{tr.dashboard.totalToCollect}</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(stats?.total_to_collect || 0)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-lg">💎</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{tr.dashboard.netBalance}</p>
                <p className={`text-2xl font-bold ${(stats?.net_balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(stats?.net_balance || 0)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                  <span className="text-yellow-600 text-lg">📊</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{tr.dashboard.activeDebts}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats?.active_debts_count || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Insights */}
        {stats && (
          <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{tr.dashboard.keyInsights}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-center p-4 bg-orange-50 rounded-lg">
                <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-orange-600 text-lg">👤</span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{tr.dashboard.personOweMost}</p>
                  <p className="font-semibold text-gray-900">
                    {stats.person_owe_most || tr.dashboard.none} 
                    {stats.person_owe_most && (
                      <span className="text-orange-600 ml-2">
                        {formatCurrency(stats.person_owe_most_amount)}
                      </span>
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-center p-4 bg-purple-50 rounded-lg">
                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-purple-600 text-lg">⏰</span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{tr.dashboard.mostOverdue}</p>
                  <p className="font-semibold text-gray-900">
                    {stats.most_overdue_debt || tr.dashboard.none} 
                    {stats.most_overdue_debt && (
                      <span className="text-purple-600 ml-2">
                        {stats.most_overdue_days} {tr.dashboard.days}
                      </span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Debts List */}
        <div className="bg-white rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">{tr.debt.yourDebts}</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {debts.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-gray-400 text-2xl">📝</span>
                </div>
                <p className="text-lg font-medium">{tr.dashboard.noDebts}</p>
                <p className="text-sm">{tr.dashboard.noDebtsDesc}</p>
              </div>
            ) : (
              debts.map((debt) => (
                <div key={debt.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${debt.debt_type === 'i_owe' ? 'bg-red-400' : 'bg-green-400'}`}></div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {debt.debt_type === 'i_owe' ? tr.debt.youOwe : tr.debt.theyOwe} {debt.person_name}
                          </p>
                          <p className="text-sm text-gray-500">{debt.description}</p>
                        </div>
                      </div>
                      <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                        <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(debt.status)}`}>
                          {getStatusText(debt.status)}
                        </span>
                        <span>{getCategoryLabel(debt.category)}</span>
                        <span>{tr.debt.due}: {formatDate(debt.due_date)}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className={`text-lg font-bold ${debt.debt_type === 'i_owe' ? 'text-red-600' : 'text-green-600'}`}>
                          {formatCurrency(debt.amount, debt.currency)}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatCurrency(debt.amount_in_try)} TRY
                        </p>
                      </div>
                      <div className="flex flex-col space-y-1">
                        {debt.status === 'active' && (
                          <button
                            onClick={() => markAsPaid(debt.id)}
                            className="px-3 py-1 bg-green-500 text-white text-sm rounded-lg hover:bg-green-600 transition-colors"
                          >
                            {tr.debt.markPaid}
                          </button>
                        )}
                        {debt.status === 'paid' && (
                          <button
                            onClick={() => markAsUnpaid(debt.id)}
                            className="px-3 py-1 bg-yellow-500 text-white text-sm rounded-lg hover:bg-yellow-600 transition-colors"
                          >
                            {tr.debt.markUnpaid}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Quick Add Modal */}
      {showAddForm && (
        <AddDebtModal 
          onClose={() => setShowAddForm(false)}
          onSuccess={fetchDashboardData}
        />
      )}

      {/* PWA Install Prompt */}
      <InstallPrompt />
    </div>
  );
};

const AddDebtModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    debt_type: 'i_owe',
    person_name: '',
    amount: '',
    currency: 'TRY',
    description: '',
    category: 'other',
    due_date: ''
  });
  const [loading, setLoading] = useState(false);
  const { showNotification } = useNotifications();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitData = {
        ...formData,
        amount: parseFloat(formData.amount),
        due_date: formData.due_date || null
      };

      await axios.post(`${API}/debts`, submitData);
      showNotification(tr.messages.success, {
        body: tr.messages.debtAdded
      });
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error adding debt:', error);
      showNotification(tr.messages.error, {
        body: tr.messages.networkError
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">{tr.debt.addDebt}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {tr.debt.debtType}
            </label>
            <select
              name="debt_type"
              value={formData.debt_type}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="i_owe">{tr.debt.iOwe}</option>
              <option value="they_owe">{tr.debt.theyOweMe}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {tr.debt.personName}
            </label>
            <input
              type="text"
              name="person_name"
              value={formData.person_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={tr.debt.personNamePlaceholder}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {tr.debt.amount}
              </label>
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                required
                min="0"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={tr.debt.amountPlaceholder}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {tr.debt.currency}
              </label>
              <select
                name="currency"
                value={formData.currency}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="TRY">{tr.currency.try}</option>
                <option value="USD">{tr.currency.usd}</option>
                <option value="EUR">{tr.currency.eur}</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {tr.debt.category}
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="personal_loan">{tr.category.personalLoan}</option>
              <option value="rent">{tr.category.rent}</option>
              <option value="shared_expense">{tr.category.sharedExpense}</option>
              <option value="business_loan">{tr.category.businessLoan}</option>
              <option value="education">{tr.category.education}</option>
              <option value="other">{tr.category.other}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {tr.debt.description}
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={tr.debt.descriptionPlaceholder}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {tr.debt.dueDateOptional}
            </label>
            <input
              type="date"
              name="due_date"
              value={formData.due_date}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              {tr.debt.cancel}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? tr.debt.adding : tr.debt.save}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Main App
function App() {
  const { token } = useAuth();

  // Register service worker
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('SW registered: ', registration);
        })
        .catch(registrationError => {
          console.log('SW registration failed: ', registrationError);
        });
    }
  }, []);

  return (
    <div className="App">
      {token ? <Dashboard /> : <LoginForm />}
    </div>
  );
}

export default function AppWithAuth() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}