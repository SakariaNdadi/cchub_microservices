FROM oven/bun:1.2.20-alpine

WORKDIR /usr/src/app

COPY package.json bun.lockb* ./

RUN bun install --ci

COPY . .

EXPOSE 4000

CMD ["bun", "run", "index.js"]