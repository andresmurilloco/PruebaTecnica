<template>
  <div>
    <form @submit.prevent="submitForm">
      <div>
        <label for="titulo">Título</label>
        <input type="text" id="titulo" v-model="titulo" required />
      </div>
      <div>
        <label for="descripcion">Descripción</label>
        <textarea id="descripcion" v-model="descripcion" required></textarea>
      </div>
      <div>
        <label for="archivo">Archivo PDF</label>
        <input type="file" id="archivo" @change="handleFileChange" required />
      </div>
      <div>
        <label for="aprobador">Aprobador (Correo electrónico)</label>
        <input type="email" id="aprobador" v-model="aprobador" required />
      </div>
      <button type="submit">Subir Documento</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      titulo: '',
      descripcion: '',
      archivo: null,
      aprobador: '',
    };
  },
  methods: {
    // Cuando se selecciona un archivo, guarda el archivo en el estado
    handleFileChange(event) {
      this.archivo = event.target.files[0];
    },
    // Enviar el formulario
    async submitForm() {
      const formData = new FormData();
      formData.append('titulo', this.titulo);
      formData.append('descripcion', this.descripcion);
      formData.append('archivo', this.archivo);
      formData.append('aprobador', this.aprobador);

      try {
        const token = localStorage.getItem('authToken'); // Obtener el token JWT del localStorage
        const response = await fetch('http://127.0.0.1:8000/api/documentos/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,  // Agregar el token JWT en el encabezado
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Error al subir el documento');
        }

        const data = await response.json();
        console.log('Documento subido con éxito', data);
        // Realiza alguna acción, por ejemplo, mostrar un mensaje o limpiar el formulario
        this.titulo = '';
        this.descripcion = '';
        this.archivo = null;
        this.aprobador = '';
      } catch (error) {
        console.error('Error:', error);
      }
    },
  },
};
</script>

<style scoped>
form {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  background-color: #0d0b0b;
  border-radius: 8px;
}

label {
  display: block;
  margin: 8px 0;
  font-weight: bold;
}

input, textarea {
  width: 100%;
  padding: 8px;
  margin-bottom: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>
