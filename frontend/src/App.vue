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
    <div v-else class="list-container">
      <h1>Listado de Documentos</h1>
      <button @click="logout">Cerrar sesión</button>
      <ul v-if="documents.length">
        <li v-for="document in documents" :key="document.id" class="document-item">
          <p><strong>Título:</strong> {{ document.titulo }}</p>
          <p><strong>Descripción:</strong> {{ document.descripcion }}</p>
          <p><strong>Estado:</strong> {{ document.estado }}</p>
          <p><strong>Aprobador:</strong> {{ document.aprobador }}</p>
          <a :href="document.archivo" target="_blank">Abrir Documento</a>

          <!-- Botones de edición, eliminación, aprobar y rechazar -->
          <div class="document-actions">
            <button @click="editDocument(document)">Editar</button>
            <button @click="deleteDocument(document.id)">Eliminar</button>
            <button @click="approveDocument(document.id)">Aprobar</button>
            <button @click="rejectDocument(document.id)">Rechazar</button>
          </div>
        </li>
      </ul>
      <p v-else>Cargando documentos...</p>

      <!-- Botón circular para abrir el modal de carga de documentos -->
      <button class="add-button" @click="openModal">+</button>

      <!-- Modal para agregar documento -->
      <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <h2>Subir Nuevo Documento</h2>
          <FormularioDoc @documentUploaded="reloadPage" />
          <button @click="closeModal">Cerrar</button>
        </div>
      </div>

      <!-- Modal de edición de documento -->
      <div v-if="isEditing" class="modal-overlay" @click.self="cancelEdit">
        <div class="modal">
          <h2>Editar Documento</h2>
          <form @submit.prevent="saveDocument">
            <div>
              <label for="titulo">Título</label>
              <input type="text" id="titulo" v-model="editableDocument.titulo" required />
            </div>
            <div>
              <label for="descripcion">Descripción</label>
              <input type="text" id="descripcion" v-model="editableDocument.descripcion" required />
            </div>
            <div class="form-actions">
              <button type="submit">Guardar Cambios</button>
              <button type="button" @click="cancelEdit">Cancelar</button>
            </div>
          </form>
        </div>
      </div>
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
      editableDocument: null,
      isEditing: false,
      isModalOpen: false,  // Estado para abrir/cerrar el modal
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

    // Función para abrir el modal
    openModal() {
      this.isModalOpen = true;
    },

    // Función para cerrar el modal
    closeModal() {
      this.isModalOpen = false;
    },

    // Función para iniciar la edición de un documento
    editDocument(document) {
      this.editableDocument = { ...document }; // Cargar datos del documento en el formulario
      this.isEditing = true; // Activar el modo de edición
    },

    // Función para guardar los cambios realizados en el documento (con PATCH)
    async saveDocument() {
      const updatedDocument = {
        titulo: this.editableDocument.titulo,
        descripcion: this.editableDocument.descripcion
      };

      try {
        const apiClient = this.getApiClient();
        await apiClient.patch(`/documentos/${this.editableDocument.id}/`, updatedDocument);
        this.fetchDocuments(); // Recargar los documentos después de la actualización
        this.cancelEdit(); // Cerrar el modal de edición
      } catch (error) {
        console.error('Error al guardar los cambios:', error.response ? error.response.data : error);
      }
    },

    // Función para cancelar la edición
    cancelEdit() {
      this.isEditing = false; // Desactivar el modo de edición
      this.editableDocument = null; // Limpiar los datos del formulario
    },

    // Función para eliminar un documento
    async deleteDocument(documentId) {
      try {
        const apiClient = this.getApiClient();
        await apiClient.delete(`/documentos/${documentId}/`);
        this.fetchDocuments(); // Recargar la lista de documentos
      } catch (error) {
        console.error('Error al eliminar el documento:', error);
      }
    },

    // Función para aprobar un documento
    async approveDocument(documentId) {
      try {
        const apiClient = this.getApiClient();
        await apiClient.patch(`/documentos/${documentId}/aprobar/`);
        this.fetchDocuments(); // Recargar documentos después de la aprobación
      } catch (error) {
        console.error('Error al aprobar el documento:', error.response ? error.response.data : error);
      }
    },

    // Función para rechazar un documento
    async rejectDocument(documentId) {
      try {
        const apiClient = this.getApiClient();
        await apiClient.patch(`/documentos/${documentId}/rechazar/`);
        this.fetchDocuments(); // Recargar documentos después del rechazo
      } catch (error) {
        console.error('Error al rechazar el documento:', error.response ? error.response.data : error);
      }
    },

    // Recargar la página al subir un documento
    reloadPage() {
      window.location.reload();
    }
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start; /* Alinea el contenido desde la parte superior */
  text-align: center;
  margin-top: 60px;
  background-color: #f4f4f9;
  padding: 20px;
  min-height: 100vh; /* Asegura que el contenedor ocupe toda la altura de la pantalla */
  width: 100%;
}

h1 {
  color: #42b983;
}

.list-container {
  width: 100%;
  max-width: 1000px; /* Ajusta el ancho máximo del contenedor */
  margin: 0 auto; /* Centra el contenedor en la pantalla */
  padding: 20px;
  background-color: #f4f4f9;
  border-radius: 8px;
}

form {
  width: 100%;
  max-width: 600px; /* Aumentar el ancho a 600px */
  margin: 20px auto; /* Centrado automático */
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

form div {
  margin-bottom: 15px;
}

form label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

form input {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

form button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  font-size: 16px;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

form button:hover {
  background-color: #38a369;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

li {
  margin: 15px 0;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: black;
}

.document-actions button {
  margin-right: 10px;
}

button {
  padding: 10px;
  background-color: red;
  color: white;
  font-size: 16px;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

button:hover {
  background-color: darkred;
}

/* Estilo para el modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal .form-actions {
  display: flex;
  justify-content: space-between;
}

/* Estilo para el botón de agregar documento */
.add-document-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #42b983;
  color: white;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px; /* Aumenté el tamaño del ícono */
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  z-index: 1001;
}

.add-document-button:hover {
  background-color: #38a369;
}

/* Estilo para el botón circular */
.add-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  background-color: #42b983;
  color: white;
  border-radius: 50%;
  font-size: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.add-button:hover {
  background-color: #38a369;
}

/* Estilo para el modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal .form-actions {
  display: flex;
  justify-content: space-between;
}

</style>
