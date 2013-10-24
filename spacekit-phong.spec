# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           spacekit-phong
Version:        0.0.1
Release:        1%{?dist}
Summary:        Phong helps you run a hackerspace

License:        GPLv3
URL:            http://spacekit.phrobo.net/phong
Source0:        %{name}-%{version}.tar.bz2

BuildRequires:  python-devel

%description
Phong helps you run a hackerspace.

%package plugin-meetings
Summary: meetings plugin for Phong
Requires: %{name} = %{version}

%description plugin-meetings
Manage your meeting minutes with Phong

%package plugin-spiff-events
Summary: Inform members about Spiff events
Requires: %{name} = %{version}

%description plugin-spiff-events
Inform members about Spiff events

%package plugin-synhak
Summary: A few bits of personality for Phong
Requires: %{name} = %{version}

%description plugin-synhak
A few bits of personality for Phong

%package plugin-sudo
Summary: Run phong commands in a sudo-like fashion
Requires: %{name} = %{version}

%description plugin-sudo
Run phong commands in a sudo-like fashion

%package plugin-documents
Summary: Build PDFs from a set of SCM repos
Requires: %{name} = %{version}

%description plugin-documents
Build PDFs from a set of SCM repos

%package plugin-cron
Summary: Run phong tasks at regular intervals
Requires: %{name} = %{version}

%description plugin-cron
Run phong tasks at regular intervals

%prep
%setup -q


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%files
%doc
# For noarch packages: sitelib
%{python_sitelib}/*
%{_bindir}/phong.py

%files plugin-meetings
%{_prefix}/lib/phong/plugins/meetings.*

%files plugin-synhak
%{_prefix}/lib/phong/plugins/synhak.*

%files plugin-spiff-events
%{_prefix}/lib/phong/plugins/events.*

%files plugin-sudo
%{_prefix}/lib/phong/plugins/sudo.*
%{_bindir}/phong-su

%files plugin-documents
%{_prefix}/lib/phong/plugins/documents.*

%files plugin-cron
%{_prefix}/lib/phong/plugins/cron.*

%changelog
