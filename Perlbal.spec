# TODO
# - split perl-devel for Devel::Peek?
#
# Conditional build:
%bcond_without	autodeps	# don't BR packages needed only for resolving deps
%bcond_with	tests		# do not perform "make test"
#
%include	/usr/lib/rpm/macros.perl
Summary:	Perlbal - Reverse-proxy load balancer and webserver
Summary(pl.UTF-8):	Perlbal - odwrotne proxy z równoważeniem obciążenia oraz serwer WWW
Name:		Perlbal
Version:	1.59
Release:	3
# same as perl
License:	GPL v1+ or Artistic
Group:		Development/Languages/Perl
Source0:	http://www.cpan.org/modules/by-authors/id/B/BR/BRADFITZ/%{name}-%{version}.tar.gz
# Source0-md5:	7d098abd4434b70f13638cdff3e2383a
Source1:	perlbal.init
Source2:	perlbal.sysconfig
Patch0:		%{name}-no_use_lib.patch
Patch1:		%{name}-test_15_webserver.patch
Patch2:		perlbal-freeport.patch
URL:		http://www.danga.com/perlbal/
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.228
%if %{with autodeps} || %{with tests}
BuildRequires:	perl-BSD-Resource
BuildRequires:	perl-Danga-Socket >= 1.44
BuildRequires:	perl-Sys-Syscall
BuildRequires:	perl-libwww
%endif
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreq	'perl(Perlbal.*)'

%description
Perlbal is a single-threaded event-based server supporting HTTP load
balancing, web serving, and a mix of the two.

One of the defining things about Perlbal is that almost everything can
be configured or reconfigured on the fly without needing to restart
the software. A basic configuration file containing a management port
enables you to easily perform operations on a running instance of
Perlbal.

%description -l pl.UTF-8
Perlbal to jednowątkowy, oparty na zdarzeniach serwer obsługujący
równoważenie obciążenia HTTP, świadczenie usług WWW oraz połączenie
obu.

Jedną z cech charakterystycznych dla Perlbala jest to, że prawie
wszystko można skonfigurować lub przekonfigurować w locie, bez
potrzeby restartu programu. Podstawowy plik konfiguracyjny zawierający
port zarządzający pozwala na łatwe wykonywanie operacji na działającej
instancji Perlbala.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make}

%if %{with tests}
# randomize the first base port a little
export TEST_TCP_FREE_PORT=$(perl -e 'print (4096 + $$) % 65536')
%{__make} test
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} pure_install \
	DESTDIR=$RPM_BUILD_ROOT

install -D %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/perlbal
install -D %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/perlbal
cp -r conf $RPM_BUILD_ROOT%{_sysconfdir}/perlbal
rm $RPM_BUILD_ROOT%{perl_vendorarch}/auto/Perlbal/.packlist

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add perlbal
%service perlbal restart

%preun
if [ "$1" = "0" ]; then
	%service -q perlbal stop
	/sbin/chkconfig --del perlbal
fi

%files
%defattr(644,root,root,755)
%doc CHANGES doc conf
%attr(755,root,root) %{_bindir}/*
%{perl_vendorlib}/*.pm
%{perl_vendorlib}/Perlbal
%{_mandir}/man?/*
%attr(754,root,root) /etc/rc.d/init.d/perlbal
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/perlbal
%dir %{_sysconfdir}/perlbal
%attr(740,root,root) %{_sysconfdir}/perlbal/*
