DOCKERFILE='''FROM python:3.12-slim
WORKDIR /app
RUN useradd --uid 10001 --create-home learner
USER 10001
EXPOSE 8010
CMD ["python", "-m", "http.server", "8010", "--bind", "0.0.0.0"]
'''
assert 'USER 10001' in DOCKERFILE and '0.0.0.0' in DOCKERFILE
assert 'API_KEY' not in DOCKERFILE
print('complete HTTP image recipe inspected; build not implied')

# Bounded exercise variation
assert '"8010"' in DOCKERFILE and 'EXPOSE 8010' in DOCKERFILE
print("Exercise variation: PASS")
