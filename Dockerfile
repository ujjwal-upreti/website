FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

WORKDIR /src

COPY ["RoleBasedAuthApp/RoleBasedAuthApp.csproj", "RoleBasedAuthApp/"]

RUN dotnet restore "RoleBasedAuthApp/RoleBasedAuthApp.csproj"

COPY . .

WORKDIR "/src/RoleBasedAuthApp"

RUN dotnet publish "RoleBasedAuthApp.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final

WORKDIR /app

COPY --from=build /app/publish .

ENV ASPNETCORE_URLS=http://0.0.0.0:10000

EXPOSE 10000

ENTRYPOINT ["dotnet", "RoleBasedAuthApp.dll"]