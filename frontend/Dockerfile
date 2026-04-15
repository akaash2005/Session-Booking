FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm install   # ← THIS is critical

COPY . .

CMD ["npm", "run", "dev"]