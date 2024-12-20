<template>
  <div id="app">
    <!-- Mostrar mensaje de carga si está procesando -->
    <div v-if="isLoading">
      <p>Cargando...</p>
    </div>

    <!-- Formulario de inicio de sesión -->
    <div v-else-if="!isAuthenticated">
      <h1>Iniciar sesión</h1>
      <form @submit.prevent="login">
        <div>
          <label for="email">Correo electrónico:</label>
          <input type="email" id="email" v-model="email" required />
        </div>
        <div>
          <label for="password">Contraseña:</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <button type="submit">Iniciar sesión</button>
        <p v-if="loginError" style="color: red;">Credenciales incorrectas. Intenta nuevamente.</p>
      </form>
    </div>

    <!-- Mostrar documentos si el usuario está autenticado -->
    <div v-else>
      <h1>Listado de Documentos</h1>
      <button @click="logout">Cerrar sesión</button>
      <ul v-if="documents.length">
        <li v-for="document in documents" :key="document.id">
          <p><strong>Título:</strong> {{ document.titulo }}</p>
          <p><strong>Descripción:</strong> {{ document.descripcion }}</p>
          <p><strong>Estado:</strong> {{ document.estado }}</p>
          <p><strong>Aprobador:</strong> {{ document.aprobador }}</p>
          <a :href="document.archivo" target="_blank">Abrir Documento</a>
        </li>
      </ul>
      <p v-else>Cargando documentos...</p>
      <FormularioDoc />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import FormularioDoc from './components/FormularioDoc.vue';

export default {
  name: 'App',
  components: {
    FormularioDoc,
  },
  data() {
    return {
      isAuthenticated: false,
      email: '',
      password: '',
      documents: [],
      loginError: false,
      isLoading: false,
    };
  },
  mounted() {
    const token = localStorage.getItem('authToken');
    if (token) {
      this.isAuthenticated = true;
      this.fetchDocuments();
    }
  },
  methods: {
    async login() {
      this.isLoading = true;
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/token/', {
          email: this.email,
          password: this.password,
        });
        localStorage.setItem('authToken', response.data.access);
        localStorage.setItem('refreshToken', response.data.refresh);
        this.isAuthenticated = true;
        this.fetchDocuments();
      } catch (error) {
        console.error('Error al iniciar sesión:', error);
        this.loginError = true;
      } finally {
        this.isLoading = false;
      }
    },
    async fetchDocuments() {
      this.isLoading = true;
      try {
        const apiClient = this.getApiClient();
        const response = await apiClient.get('/documentos');
        this.documents = response.data;        
      } catch (error) {
        console.error('Error al obtener documentos:', error);
      } finally {
        this.isLoading = false;
      }
    },
    logout() {
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      this.isAuthenticated = false;
      this.documents = [];
    },
    getApiClient() {
      const apiClient = axios.create({
        baseURL: 'http://127.0.0.1:8000/api',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      apiClient.interceptors.response.use(
        response => response,
        async error => {
          if (
            error.response.status === 401 &&
            error.response.data.code === 'token_not_valid'
          ) {
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              try {
                const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
                  refresh: refreshToken,
                });
                localStorage.setItem('authToken', response.data.access);
                error.config.headers.Authorization = `Bearer ${response.data.access}`;
                return apiClient.request(error.config); // Reintenta la solicitud
              } catch (refreshError) {
                console.error('Error al renovar el token:', refreshError);
                this.logout();
              }
            }
          }
          return Promise.reject(error);
        }
      );

      return apiClient;
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  margin-top: 60px;
}

form {
  max-width: 300px;
  margin: 0 auto;
}

form div {
  margin-bottom: 15px;
}

form label {
  display: block;
  margin-bottom: 5px;
}

form input {
  width: 100%;
  padding: 8px;
  font-size: 14px;
}

form button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  font-size: 16px;
  border: none;
  cursor: pointer;
}

form button:hover {
  background-color: #38a369;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin: 15px 0;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

h1 {
  color: #42b983;
}

button {
  padding: 10px;
  background-color: red;
  color: white;
  font-size: 16px;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: darkred;
}
</style>
