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

BuildArch:      noarch
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
%{_datadir}/phong/plugins/meetings.*

%files plugin-synhak
%{_datadir}/phong/plugins/synhak.*

%files plugin-spiff-events
%{_datadir}/phong/plugins/events.*

%changelog
