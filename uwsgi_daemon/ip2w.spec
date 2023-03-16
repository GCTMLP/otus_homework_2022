License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/3/
Source0:        otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch		
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd, bash
Requires: python-requests, nginx
Summary: Weather uWSGI daemon.


%description

Weather uWSGI daemon. Determines the city by IP and get information about the weather in given city

Git version: %{git_version} (branch: %{git_branch})

%define __etcdir    /usr/local/etc/
%define __logdir    /var/log/
%define __bindir    /usr/local/ip2w/
%define __systemddir	/usr/lib/systemd/system/
%define __nginx    /etc/nginx/


%prep
rm -rf %{buildroot}
%setup -q -n otus-%{current_datetime}

%install
[ "%{buildroot}" != "/" && rm -rf {buildroot}] 
%{__mkdir} -p %{buildroot}%{__systemddir}
%{__install} -pD -m 644 %{name}.service %{buildroot}%{__systemddir}%{name}.service

%{__mkdir} -p %{buildroot}%{__bindir }
%{__install} -pD -m 755 %{name}.py %{buildroot}%{__bindir}%{name}.py

%{__mkdir} -p %{buildroot}%{__etcdir}
%{__install} -pD -m 644 %{name}.ini %{buildroot}%{__etcdir}%{name}.ini

%{__mkdir} -p %{buildroot}%{__nginx}
%{__install} -pD -m 644 %{name}_nginx.conf %{buildroot}%{__nginx}%{name}_nginx.conf

%{__mkdir} -p %{buildroot}%{__logdir}

%post
%systemd_post %{name}.service
systemctl daemon-reload
nginx -s quit
nginx -c %{__nginx}%{name}_nginx.conf

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service
nginx -s quit
nginx

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}

%files
%{__logdir}
%{__bindir}
%{__systemddir}
%{__etcdir}
%{__nginx}
